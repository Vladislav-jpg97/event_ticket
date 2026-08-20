from sqlalchemy import select, func

from backend.models import Review
from backend.repository.base import BaseRepository
from backend.repository.mixins import (
    AddRepositoryMixin,
    DeleteRepositoryMixin,
    RetrieveRepositoryMixin,
)


class ReviewRepository(
    BaseRepository[Review],
    AddRepositoryMixin[Review],
    DeleteRepositoryMixin[Review],
    RetrieveRepositoryMixin[Review],
):
    model = Review

    async def get_by_event_and_author(
            self,
            event_id: int,
            author_id: int,
    ) -> Review | None:
        stmt = select(Review).where(Review.event_id == event_id, Review.author_id == author_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_paginated_reviews(
            self,
            event_id: int,
            page: int,
            size: int,
    ):
        count_query = select(func.count(Review.id)).where(Review.event_id == event_id)
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        skip = (page - 1) * size

        stmt = (
            select(Review)
            .where(Review.event_id == event_id)
            .offset(skip)
            .limit(size)
        )
        result = await self.session.execute(stmt)
        reviews = result.scalars().all()

        return list(reviews), total

    async def get_average_rating(self, event_id: int) -> float | None:
        stmt = select(func.avg(Review.rating)).where(Review.event_id == event_id)
        result = await self.session.execute(stmt)
        avg_value = result.scalar()

        if avg_value is not None:
            return round(float(avg_value), 2)
        return None
