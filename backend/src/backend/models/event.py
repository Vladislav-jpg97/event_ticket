from datetime import datetime
from decimal import Decimal
from typing import List, TYPE_CHECKING

from sqlalchemy import Table, Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.enums import EventStatus
from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.category import Category
    from backend.models.user import User
    from backend.models.tag import Tag

event_tags = Table(
    'event_tags',
    Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True),
)


class Event(Base):
    __tablename__ = 'events'

    title: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[str] = mapped_column(nullable=False)
    venue: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    starts_at: Mapped[datetime] = mapped_column(nullable=False)
    ends_at: Mapped[datetime] = mapped_column(nullable=False)
    capacity: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[EventStatus] = mapped_column()

    # Статистика и счетчики
    tickets_sold: Mapped[int] = mapped_column(default=0, nullable=False)
    available_seats: Mapped[int] = mapped_column(nullable=False)
    avg_rating: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True, default=None)
    views: Mapped[int] = mapped_column(default=0, nullable=False)

    organizer_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    # Связи (Relationships)
    organizer: Mapped["User"] = relationship(foreign_keys=[organizer_id])
    category: Mapped["Category"] = relationship(back_populates="events")
    tags: Mapped[List["Tag"]] = relationship(secondary=event_tags, back_populates="events")

    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="event", cascade="all, delete-orphan")