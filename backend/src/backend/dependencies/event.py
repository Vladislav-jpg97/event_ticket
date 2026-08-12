from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies.database import SessionDep, get_db
from backend.models import User
from backend.repository.event import EventRepository
from backend.repository.tag import TagRepository
from backend.services.event import EventService
from backend.services.tag import TagService


async def get_event_repo(session: SessionDep) -> EventRepository:
    return EventRepository(session)

EventRepoDep = Annotated[EventRepository, Depends(get_event_repo)]

async def get_event_service(
        session: SessionDep,
        event_repo: EventRepoDep,
) -> EventService:
    return EventService(session=session, event_repo=event_repo)

EventServiceDep = Annotated[EventService, Depends(get_event_service)]
