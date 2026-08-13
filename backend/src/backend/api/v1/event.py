from fastapi import APIRouter
from fastapi.params import Depends, Query
from starlette import status

from backend.dependencies.event import EventServiceDep
from backend.dependencies.user_auth import require_role, UserRole, get_current_user
from backend.models import User
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
async def get_events(
        service: EventServiceDep,
        page: int = Query(1, ge=1, description="номер страницы"),
        size: int = Query(10, ge=1, le=100, description="кол-во эл на странице"),
        current_user=Depends(get_current_user),

) -> dict:
    res = await service.get_paginated_events(
        page=page,
        size=size,
        current_user=current_user
    )
    return res


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


# --- Сначала универсальный одиночный параметр пути (slug) ---
@router.get(
    "/{slug}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Детали события + счётчик просмотров"
)
async def get_event_and_views(
        slug: str,
        event_service: EventServiceDep,
):
    return await event_service.get_event_detail_by_slug(slug)


# --- Затем составные пути с дополнительными сегментами ---
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