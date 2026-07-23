from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.base import Base

class Category(Base):

    __tablename__ = 'categories'

    name : Mapped[str] = mapped_column(unique=True,nullable=False)
    slug : Mapped[str] = mapped_column(unique=True,nullable=False)

    events : Mapped[List["Event"]] = relationship(back_populates="category")