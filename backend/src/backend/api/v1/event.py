from fastapi import APIRouter
from starlette import status

from backend.schemas.auth import UserResponse
from backend.schemas.event import PaginatedEventResponse, EventResponse, EventCreate
from backend.schemas.review import ReviewResponse, ReviewCreate
from backend.schemas.ticket import TicketResponse, TicketCreate

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
    summary="Создание событий"
)
async def create_event(
        request: EventCreate
) -> EventResponse:
    pass


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
