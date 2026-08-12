from fastapi import APIRouter
from fastapi.params import Depends
from starlette import status

from backend.dependencies.event import EventServiceDep
from backend.dependencies.user_auth import require_role, UserRole
from backend.models import User
from backend.schemas.event import PaginatedEventResponse, EventResponse, EventCreate
from backend.schemas.review import ReviewResponse, ReviewCreate
from backend.schemas.ticket import TicketResponse, TicketCreate
from backend.services.event import EventService

router = APIRouter(
    prefix="/events",
    tags=["events"],
)


@router.get(
    "/",
    response_model=PaginatedEventResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение всех событий"
)
async def get_events() -> PaginatedEventResponse:
    pass


@router.post(
    "/",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_event(
    event_in: EventCreate,
    event_service: EventServiceDep,
    current_user: User = Depends(require_role(UserRole.ORGANIZER, UserRole.ADMIN)),
):
    event = await event_service.create_event(
        event_data=event_in,
        organizer_id=current_user.id,
        tag_names=event_in.tags)

    return event


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить одно событие"
)
async def get_event_by_id(
        event_id: int
) -> EventResponse:
    pass


@router.get(
    "/{event_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение отзывов о конкретном событии"
)
async def get_event_reviews() -> ReviewResponse:
    pass


@router.post(
    "/{id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Оставить отзыв о событии"
)
async def create_event_reviews(
        event_id: int,
        request: ReviewCreate
) -> ReviewResponse:
    pass


@router.post(
    "/{event_id}/register",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Покупка билета / бронирование мест на событие"
)
async def register_event(
        event_id: int,
        request: TicketCreate
) -> TicketResponse:
    pass
