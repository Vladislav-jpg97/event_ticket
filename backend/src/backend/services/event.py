from datetime import datetime, timezone
from itertools import count

from fastapi import HTTPException
from redis import Redis
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.core.enums import EventStatus, Role
from backend.models import Event, User
from backend.repository.event import EventRepository
from backend.schemas.event import EventUpdate
from backend.utils.slug import slug_generator


class EventService:
    def __init__(
            self,
            session: AsyncSession,
            event_repo: EventRepository,
            redis: Redis,
    ):
        self.session = session
        self.event_repo = event_repo
        self.redis = redis

    async def create_event(
            self,
            event_data,
            organizer_id: int,
            tag_names: list[str] = None,
    ) -> Event:
        base_slug = slug_generator.generate(event_data.title)
        unique_slug = base_slug
        counter = 2
        while True:
            existing = await self.event_repo.get_by_slug(unique_slug)
            if not existing:
                break
            unique_slug = f"{base_slug}-{counter}"
            counter += 1

        tags = []
        if tag_names:
            tags = await self.event_repo.get_or_create_tags(tag_names)

        new_event = Event(
            title=event_data.title,
            description=event_data.description,
            slug=unique_slug,
            category_id=event_data.category_id,
            organizer_id=organizer_id,
            starts_at=event_data.starts_at,
            ends_at=event_data.ends_at,
            capacity=event_data.capacity,
            available_seats=event_data.capacity,
            tickets_sold=0,
            views=0,
            price=event_data.price,
            venue=event_data.venue,
            city=event_data.city,
            status=EventStatus.DRAFT,
            tags=tags,
        )
        created_event = await self.event_repo.add(new_event)
        await self.session.commit()

        return await self.event_repo.get_event_with_relations(created_event.id)

    async def get_paginated_events(
            self,
            page: int,
            size: int,
            current_user=None,
    ) -> dict:
        user_id = current_user.id if current_user else None
        is_organizer = current_user and (current_user.role in (Role.ORGANIZER, Role.ADMIN))

        events, total = await self.event_repo.get_paginated_events(
            page=page,
            size=size,
            user_id=user_id,
            is_organizer=is_organizer,
        )
        pages = (total + size - 1) // size if size > 0 else 0
        return {
            "items": events,
            "total": total,
            "page": page,
            "pages": pages if pages > 0 else 1,
        }

    async def get_event_detail_by_slug(self, slug: str) -> Event:
        event = await self.event_repo.get_by_slug_with_relations(slug)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        views_count = await self.redis.incr(f"event:views:{event.id}")
        event.views = views_count

        return event

    async def update_event(self, slug: str, body: EventUpdate, current_user: User):
        # Подгружаем событие вместе со связанными таблицами (категория, теги и т.д.)
        event = await self.event_repo.get_by_slug_with_relations(slug)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        # Проверка прав (организатор или админ)
        if event.organizer_id != current_user.id and current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this event."
            )

        # Проверка статуса (редактировать можно только черновики)
        if event.status != EventStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only DRAFT events can be updated"
            )

        # Получаем только те поля, которые реально передал клиент в запросе
        update_data = body.model_dump(exclude_unset=True)

        # Перегенерация slug, если изменился title
        if "title" in update_data:
            base_slug = slug_generator.generate(update_data["title"])
            unique_slug = base_slug
            counter = 1

            while await self.event_repo.get_by_slug(unique_slug):
                if unique_slug == event.slug:
                    break
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            update_data["slug"] = unique_slug

        # Обработка тегов, если они переданы в запросе
        if "tags" in update_data:
            tag_names = update_data.pop("tags")
            if tag_names is not None:
                event.tags = await self.event_repo.get_or_create_tags(tag_names)

        # Получаем ключи реальных колонок таблицы базы данных
        mapper = inspect(Event)
        column_keys = mapper.columns.keys()

        # Применяем изменения к модели
        for field, value in update_data.items():
            if field in column_keys:
                # Если category_id пришел пустым/None, не перезаписываем существующее значение в базе
                if field == "category_id" and value is None:
                    continue

                # Сбрасываем таймзону для datetime (совместимость с TIMESTAMP WITHOUT TIME ZONE)
                if isinstance(value, datetime):
                    if value.tzinfo is not None:
                        value = value.astimezone(timezone.utc).replace(tzinfo=None)

                setattr(event, field, value)

        # Сохраняем изменения в базе данных
        self.session.add(event)
        await self.session.commit()

        # Возвращаем обновленное событие со всеми связями
        return await self.event_repo.get_event_with_relations(event.id)
