from sqlalchemy import select
from sqlalchemy.orm import joinedload

from backend.models import Ticket, Event
from backend.repository.base import BaseRepository
from backend.repository.mixins import (
    AddRepositoryMixin,
    DeleteRepositoryMixin,
    RetrieveRepositoryMixin,
    UpdateRepositoryMixin,
)


class TicketRepository(
    BaseRepository[Ticket],
    AddRepositoryMixin[Ticket],
    UpdateRepositoryMixin[Ticket],
    DeleteRepositoryMixin[Ticket],
    RetrieveRepositoryMixin[Ticket],
):
    model = Ticket

    async def get_my_tickets_paginated(
            self,
            user_id: int,
            offset: int = 0,
            limit: int = 10
    ):
        stmt = (
            select(Ticket)
            .options(joinedload(Ticket.event))
            .join(Event, Ticket.event_id == Event.id)
            .where(Ticket.buyer_id == user_id)
            .order_by(Event.starts_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()