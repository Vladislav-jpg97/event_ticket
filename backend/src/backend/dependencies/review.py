from typing import Annotated
from fastapi import Depends

from backend.dependencies.database import SessionDep
from backend.repository.review import ReviewRepository
from backend.services.review import ReviewService

# Импортируем готовые зависимости, созданные в других модулях
from backend.dependencies.event import EventRepoDep
from backend.dependencies.ticket import TicketRepoDep


async def get_review_repo(session: SessionDep) -> ReviewRepository:
    return ReviewRepository(session)

ReviewRepoDep = Annotated[ReviewRepository, Depends(get_review_repo)]


async def get_review_service(
        session: SessionDep,
        review_repo: ReviewRepoDep,
        event_repo: EventRepoDep,
        ticket_repo: TicketRepoDep
) -> ReviewService:
    return ReviewService(
        session=session,
        review_repo=review_repo,
        event_repo=event_repo,
        ticket_repo=ticket_repo
    )

ReviewServiceDep = Annotated[ReviewService, Depends(get_review_service)]