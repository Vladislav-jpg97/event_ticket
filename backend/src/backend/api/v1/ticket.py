from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from starlette.responses import StreamingResponse

from backend.dependencies.user_auth import get_current_user
from backend.dependencies.ticket import TicketServiceDep
from backend.models import User
from backend.schemas.ticket import TicketCreate, TicketResponse

router = APIRouter(tags=["Tickets"])


@router.post(
    "/events/{slug}/tickets",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Покупка билета на событие",
)
async def buy_ticket(
        slug: str,
        body: TicketCreate,
        service: TicketServiceDep,
        current_user: User = Depends(get_current_user),
):
    ticket = await service.buy_ticket(
        slug=slug,
        user_id=current_user.id,
        quantity=body.quantity,
    )
    return ticket


@router.get(
    "/tickets/me",
    response_model=list[TicketResponse],
    status_code=status.HTTP_200_OK,
    summary="Просмотр списка своих купленных билетов/броней",
)
async def get_user_tickets(
        service: TicketServiceDep,
        page: int = Query(1, ge=1, description="Номер страницы"),
        size: int = Query(1, ge=1, le=100, description="Количество элементов на странице"),
        current_user: User = Depends(get_current_user),

) -> list[TicketResponse]:
    return await service.get_user_tickets(
        user_id=current_user.id,
        page=page,
        size=size,
    )


@router.get("/{ticket_id}/qr", response_class=StreamingResponse)
async def get_ticket_qr(
        ticket_id: int,
        ticket_service: TicketServiceDep,

        current_user: User = Depends(get_current_user),
):
    return await ticket_service.gen_ticket_qr(ticket_id=ticket_id, user_id=current_user.id)


@router.delete(
    "/tickets/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отмена билета/бронирования",
)
async def delete_user_ticket(
        ticket_id: int,
        service: TicketServiceDep,
        current_user: User = Depends(get_current_user),

) -> None:
    return await service.cancel_ticket(ticket_id, current_user.id)
