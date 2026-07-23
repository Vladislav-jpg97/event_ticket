from sqlalchemy import Text, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class Review(Base):
    __tablename__ = 'reviews'

    event_id: Mapped[int] = mapped_column(ForeignKey('events.id'))
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    rating: Mapped[int]
    comment: Mapped[str] = mapped_column(Text, nullable=True)

    # Уникальное составное ограничение задается здесь через __table_args__
    __table_args__ = (
        UniqueConstraint(
            'event_id',
            'author_id',
            name='uq_event_author_review'
        ),
    )