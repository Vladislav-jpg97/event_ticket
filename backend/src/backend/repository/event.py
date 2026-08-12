from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.models import Event
from backend.models.tag import Tag
from backend.repository.base import BaseRepository
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

    async def get_by_slug(self, slug: str) -> Event | None:
        stmt = select(Event).where(Event.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_event_with_relations(self, event_id: int) -> Event | None:
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
        return result.scalars().first()

