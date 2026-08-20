from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Query
from starlette import status

from backend.dependencies.event import EventServiceDep
from backend.dependencies.user_auth import require_role, UserRole, get_current_user
from backend.models import User
from backend.schemas.event import PaginatedEventResponse, EventResponse, EventCreate, EventUpdate, EventShortResponse, \
    EventStatusResponse, EventFilterParams
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
    summary="Получить список событий с фильтрами и пагинацией"
)
async def get_events(
        service: EventServiceDep,
        current_user: User = Depends(get_current_user),
        page: int = Query(1, ge=1, description="Номер страницы"),
        size: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
        filters: EventFilterParams = Depends(),
):
    result = await service.get_paginated_events(
        current_user=current_user,
        filters=filters,
        page=page,
        size=size,
    )
    return result


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


@router.get("/popular", response_model=list[EventShortResponse])
async def get_popular(
        service: EventServiceDep,
):
    return await service.get_popular_events()


# --- Сначала универсальный одиночный параметр пути (slug) ---
@router.get(
    "/{slug}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Детали события + счётчик просмотров"
)
async def get_event_and_views(
        slug: str,
        service: EventServiceDep,
):
    return await service.get_event_detail_by_slug(slug)


@router.patch("/{slug}", response_model=EventResponse)
async def update_event(
        slug: str,
        body: EventUpdate,
        service: EventServiceDep,
        current_user: User = Depends(get_current_user),

):
    updated_event = await service.update_event(
        slug=slug,
        body=body,
        current_user=current_user
    )
    return updated_event


# --- Затем составные пути с дополнительными сегментами ---
@router.get(
    "/{slug}/status",
    response_model=EventStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение статистики продаж конкретного события"
)
async def get_event_status(
        slug: str,
        service: EventServiceDep,
        current_user: User = Depends(get_current_user),
) -> EventStatusResponse:
    return await service.get_event_status(
        slug=slug,
        current_user=current_user
    )




@router.post(
    "/{event_id}/publish",
    status_code=status.HTTP_200_OK,
    summary="Публикация События"
)
async def publish_event_endpoint(
        event_id: int,
        service: EventServiceDep,
        current_user: User = Depends(get_current_user),
):
    event = await service.event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return await service.publish_event(event, current_user)


@router.post(
    "/{event_id}/cancel",
    status_code=status.HTTP_200_OK,
    summary="Удаления События"
)
async def cancel_event(
        event_id: int,
        service: EventServiceDep,
        current_user: User = Depends(get_current_user),
):
    event = await service.event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return await service.cancel_event(event, current_user)
