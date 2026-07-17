from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.src.backend.models.base import Base


class Category(Base):

    __tablename__ = 'categories'

    name : Mapped[str] = mapped_column(unique=True,not_null=True)
    slug : Mapped[str] = mapped_column(unique=True,not_null=True)

    events : Mapped[List["Event"]] = relationship(back_populates="category")