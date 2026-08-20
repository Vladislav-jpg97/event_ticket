from datetime import datetime, timezone
from sqlalchemy import Text, UniqueConstraint, ForeignKey, CheckConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey('events.id', ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))
    rating: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint(
            'event_id',
            'author_id',
            name='uq_event_author_review'
        ),
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range")
    )