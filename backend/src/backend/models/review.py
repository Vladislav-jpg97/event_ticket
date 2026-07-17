from sqlalchemy import Text, UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column

from backend.src.backend.models.base import Base


class Review(Base):
    __tablename__ = 'reviews'

    event_id : Mapped[int] = mapped_column(foreign_key='events.id')
    author_id: Mapped[int] = mapped_column(foreign_key='users.id')
    rating: Mapped[int]
    comment: Mapped[str] = mapped_column(Text,nullable=True)

    __mapper_args__ = {
        UniqueConstraint(
            'event_id',
            'author_id',
            name='uq_event_author_review'
        )
    }