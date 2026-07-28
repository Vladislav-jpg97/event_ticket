from fastapi import APIRouter, HTTPException
from starlette import status

from backend.schemas.ticket import TicketResponse

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


@router.get(
    "/me",
    response_model=list[TicketResponse],
    status_code=status.HTTP_200_OK,
    summary="Просмотр списка своих купленных билетов/броней",
)
async def get_user_tickets() -> list[TicketResponse]:
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отмена билета/бронирования"
)
async def delete_user_ticket(ticket_id: int) -> None:
    raise HTTPException(status_code=501, detail="Not Implemented")