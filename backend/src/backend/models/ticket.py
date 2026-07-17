from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped,mapped_column

from backend.src.backend.core.enums import TicketStatus
from backend.src.backend.models.base import Base


class Ticket(Base):
    __tablename__ = 'tickets'
    uuid: Mapped[str] = mapped_column(unique=True)

    event_id: Mapped[int] = mapped_column(ForeignKey('events.id'), nullable=False)
    buyer_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    quantity: Mapped[int] = mapped_column(nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    status: Mapped[TicketStatus] = mapped_column(default=TicketStatus.PENDING)