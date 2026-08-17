from typing import Annotated
from fastapi import Depends

from backend.core.cache import RedisDep
from backend.dependencies.database import SessionDep
from backend.repository.event import EventRepository
from backend.services.event import EventService


async def get_event_repo(session: SessionDep) -> EventRepository:
    return EventRepository(session)

EventRepoDep = Annotated[EventRepository, Depends(get_event_repo)]

async def get_event_service(
        session: SessionDep,
        event_repo: EventRepoDep,
        redis: RedisDep,
) -> EventService:
    return EventService(
        session=session,
        event_repo=event_repo,
        cache=redis
    )

EventServiceDep = Annotated[EventService, Depends(get_event_service)]