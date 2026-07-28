from fastapi import APIRouter, HTTPException
from starlette import status
from backend.schemas.review import ReviewResponse, ReviewCreate

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"]
)

@router.get(
    "/event/{event_id}",
    response_model=list[ReviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Получение отзывов о событии",
)
async def get_event_reviews(event_id: int) -> list[ReviewResponse]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not Implemented"
    )

@router.post(
    "/event/{event_id}",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Оставить отзыв о событии"
)
async def create_review(event_id: int, review_data: ReviewCreate) -> ReviewResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not Implemented"
    )