from fastapi import APIRouter, HTTPException, Query, Depends
from starlette import status

from backend.dependencies.review import ReviewServiceDep
from backend.dependencies.user_auth import get_current_user
from backend.models import User
from backend.schemas.review import ReviewResponse, ReviewCreate

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"]
)


@router.get("/{slug}/reviews", summary="Получить список отзывов к событию")
async def get_event_reviews(
        slug: str,
        review_service: ReviewServiceDep,
        page: int = Query(1, ge=1, description="Номер страницы"),
        size: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
):
    return await review_service.get_event_reviews(slug=slug, page=page, size=size)


@router.post("/{slug}/reviews", status_code=status.HTTP_201_CREATED, summary="Оставить отзыв о событии")
async def create_review(
        review_service: ReviewServiceDep,
        slug: str,
        rating: float = Query(..., ge=1, le=5, description="Оценка от 1 до 5"),
        comment: str = Query(..., min_length=1, max_length=1000, description="Текст отзыва"),
        current_user: User = Depends(get_current_user),
):
    return await review_service.create_review(
        slug=slug,
        author_id=current_user.id,
        rating=rating,
        comment=comment
    )


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить отзыв")
async def delete_review(
        review_id: int,
        review_service: ReviewServiceDep,
        current_user=Depends(get_current_user),
):
    await review_service.delete_review(review_id=review_id, current_user=current_user)
    return None
