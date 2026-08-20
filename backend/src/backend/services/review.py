from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.core.enums import Role
from backend.dependencies.user_auth import UserRole
from backend.models import Review
from backend.repository.event import EventRepository
from backend.repository.review import ReviewRepository
from backend.repository.ticket import TicketRepository


class ReviewService:
    def __init__(
            self,
            session: AsyncSession,
            review_repo: ReviewRepository,
            event_repo: EventRepository,
            ticket_repo: TicketRepository
    ):
        self.session = session
        self.event_repo = event_repo
        self.ticket_repo = ticket_repo
        self.review_repo = review_repo

    async def create_review(
            self,
            slug: str,
            author_id: int,
            rating: float,
            comment: str
    ):
        event = await self.event_repo.get_by_slug(slug)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        ticket = await self.ticket_repo.get_paid_ticket_by_user_and_event(author_id, event.id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь должен купить билет на это событие"
            )

        check_review = await self.review_repo.get_by_event_and_author(event.id, author_id)
        if check_review:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Вы уже оставили отзыв на это событие"
            )

        new_review = Review(
            event_id=event.id,
            author_id=author_id,
            rating=rating,
            comment=comment
        )
        res = await self.review_repo.add(new_review)
        await self.session.commit()
        return res

    async def get_event_reviews(
            self,
            slug: str,
            page: int,
            size: int
    ):
        event = await self.event_repo.get_by_slug(slug)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        reviews, total = await self.review_repo.get_paginated_reviews(
            event_id=event.id,
            page=page,
            size=size
        )
        avg_rating = await self.review_repo.get_average_rating(event.id)

        return {
            "items": reviews,
            "total": total,
            "page": page,
            "size": size,
            "avg_rating": avg_rating
        }

    async def delete_review(
            self,
            review_id: int,
            current_user
    ):
        # 1. Ищем отзыв
        review = await self.review_repo.get_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # 2. Проверяем права: удалить может либо автор, либо админ через UserRole
        is_author = review.author_id == current_user.id
        is_admin = current_user.role == Role.ADMIN

        if not (is_author or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет прав на удаление этого отзыва"
            )

        # 3. Удаляем через репозиторий и подтверждаем транзакцию
        await self.review_repo.delete(review)
        await self.session.commit()