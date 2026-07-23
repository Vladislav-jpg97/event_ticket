from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import Table, Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.enums import EventStatus
from backend.models.base import Base
from backend.models.category import Category

event_tags = Table('event_tags',
                   Base.metadata,
                   Column('event_id', Integer, ForeignKey('events.id'),primary_key=True),
                   Column('tag_id', Integer, ForeignKey('tags.id'),primary_key=True),
                   )

class Event(Base):

    __tablename__ = 'events'

    title: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(unique=True,index=True)
    description: Mapped[str] = mapped_column(nullable=False)
    venue: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    starts_at: Mapped[datetime] = mapped_column(nullable=False)
    ends_at: Mapped[datetime] = mapped_column(nullable=False)
    capacity: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[EventStatus] = mapped_column()
    organizer_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    category: Mapped["Category"] = relationship(back_populates="events")
    tags : Mapped[List["Tag"]] = relationship(secondary=event_tags,back_populates="events")
