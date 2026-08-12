from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.enums import EventStatus
from backend.models import Event
from backend.repository.event import EventRepository
from backend.utils.slug import slug_generator


class EventService:
    def __init__(self, session: AsyncSession, event_repo: EventRepository):
        self.session = session
        self.event_repo = event_repo

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

        return await self.event_repo.get_event_with_relations(created_event.id)