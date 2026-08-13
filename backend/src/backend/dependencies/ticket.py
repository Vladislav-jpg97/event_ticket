from typing import Annotated
from fastapi import Depends

from backend.core.cache import CacheServiceDep 
from backend.dependencies.database import SessionDep
from backend.dependencies.event import EventRepoDep
from backend.repository.ticket import TicketRepository
from backend.services.ticket import TicketService


async def get_ticket_repo(session: SessionDep) -> TicketRepository:
    return TicketRepository(session)


TicketRepoDep = Annotated[TicketRepository, Depends(get_ticket_repo)]


async def get_ticket_service(
        session: SessionDep,
        ticket_repo: TicketRepoDep,
        event_repo: EventRepoDep,
        cache_service: CacheServiceDep,
) -> TicketService:
    return TicketService(
        session=session,
        ticket_repo=ticket_repo,
        event_repo=event_repo,
        redis_client=cache_service,
    )


TicketServiceDep = Annotated[TicketService, Depends(get_ticket_service)]