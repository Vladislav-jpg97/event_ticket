
from backend.models import Ticket
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