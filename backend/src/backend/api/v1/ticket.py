from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from backend.dependencies.user_auth import get_current_user
from backend.dependencies.ticket import TicketServiceDep
from backend.models import User
from backend.schemas.ticket import TicketCreate, TicketResponse

router = APIRouter(tags=["Tickets"])

CurrentActiveUser = Annotated[User, Depends(get_current_user)]


@router.post(
    "/events/{slug}/tickets",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Покупка билета на событие",
)
async def buy_ticket_endpoint(
    slug: str,
    body: TicketCreate,
    current_user: CurrentActiveUser,
    service: TicketServiceDep,
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
    current_user: CurrentActiveUser,
) -> list[TicketResponse]:
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.delete(
    "/tickets/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отмена билета/бронирования",
)
async def delete_user_ticket(
    ticket_id: int,
    current_user: CurrentActiveUser,
) -> None:
    raise HTTPException(status_code=501, detail="Not Implemented")