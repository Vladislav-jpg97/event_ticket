from datetime import datetime
from decimal import Decimal
import uuid

from sqlalchemy import ForeignKey, Numeric, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.enums import TicketStatus
from backend.models.base import Base


class Ticket(Base):
    __tablename__ = 'tickets'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )

    event_id: Mapped[int] = mapped_column(ForeignKey('events.id'), nullable=False)
    buyer_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    quantity: Mapped[int] = mapped_column(nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    status: Mapped[TicketStatus] = mapped_column(default=TicketStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    event: Mapped["Event"] = relationship("Event", back_populates="tickets")