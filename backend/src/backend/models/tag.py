from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.backend.models.base import Base
from backend.src.backend.models.event import event_tags


class Tag(Base):
    __tablename__ = 'tags'
    name: Mapped[str] = mapped_column(unique=True, not_null=True)

    events : Mapped[List["Event"]] = relationship(secondary=event_tags,back_populates="tags")
