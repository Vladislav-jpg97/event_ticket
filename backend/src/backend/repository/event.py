from datetime import datetime

from sqlalchemy import select, or_, func, and_
from sqlalchemy.orm import selectinload, joinedload, Query

from backend.core.enums import EventStatus
from backend.models import Event, Category
from backend.models.tag import Tag
from backend.repository.base import BaseRepository
from backend.repository.filters import apply_event_filters, apply_event_sorting
from backend.repository.mixins import (
    AddRepositoryMixin,
    DeleteRepositoryMixin,
    RetrieveRepositoryMixin,
    UpdateRepositoryMixin,
)


class EventRepository(
    BaseRepository[Event],
    AddRepositoryMixin[Event],
    UpdateRepositoryMixin[Event],
    DeleteRepositoryMixin[Event],
    RetrieveRepositoryMixin[Event],
):
    model = Event

    async def get_or_create_tags(self, tag_names: list[str]) -> list[Tag]:
        if not tag_names:
            return []

        stmt = select(Tag).where(Tag.name.in_(tag_names))
        result = await self.session.execute(stmt)
        existing_tags = result.scalars().all()

        existing_names = {tag.name for tag in existing_tags}
        new_names = [name for name in tag_names if name not in existing_names]

        new_tags = []
        for name in new_names:
            new_tag = Tag(name=name)
            self.session.add(new_tag)
            new_tags.append(new_tag)

        if new_tags:
            await self.session.flush()

        return list(existing_tags) + new_tags

    async def get_by_slug(self, slug: str):
        stmt = select(Event).where(Event.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_event_with_relations(self, event_id: int ) -> Event | None:
        query = (
            select(Event)
            .options(
                selectinload(Event.category),
                selectinload(Event.organizer),
                selectinload(Event.tags),
            )
            .where(Event.id == event_id)
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_by_slug_with_relations(self, slug: str) -> Event | None:
        query = (
            select(Event)
            .options(
                selectinload(Event.category),
                selectinload(Event.organizer),
                selectinload(Event.tags),
            )
            .where(Event.slug == slug.strip())
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_paginated_events(self, page, size, user_id, is_organizer, filters):
        # 1. Базовая видимость
        visibility_condition = (
            or_(Event.status == EventStatus.PUBLISHED, Event.organizer_id == user_id)
            if (user_id and is_organizer)
            else Event.status == EventStatus.PUBLISHED
        )

        # 2. Считаем total
        count_stmt = select(func.count(Event.id)).where(visibility_condition)
        count_stmt = apply_event_filters(count_stmt, filters)
        total = (await self.session.execute(count_stmt)).scalar_one()

        # 3. Основной запрос
        stmt = select(Event).where(visibility_condition)
        stmt = apply_event_filters(stmt, filters)

        # Сортировка, связи и пагинация
        stmt = apply_event_sorting(stmt, filters.sort)
        stmt = (
            stmt.options(
                joinedload(Event.category),
                joinedload(Event.organizer),
                selectinload(Event.tags),
            )
            .offset((page - 1) * size)
            .limit(size)
        )

        events = (await self.session.execute(stmt)).unique().scalars().all()
        return list(events), total

    async def get_event_with_lock(self, event_id: int) -> Event | None:
        query = (
            select(Event)
            .where(Event.id == event_id)
            .with_for_update()
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_popular(self, limit: int = 10):
        query = (
            select(Event)
            .where(Event.status == EventStatus.PUBLISHED)
            .order_by(Event.views.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
