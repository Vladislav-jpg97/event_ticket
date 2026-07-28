from fastapi import APIRouter, HTTPException
from starlette import status
from backend.schemas.category import CategoryResponse

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@router.get(
    "/",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Получение всех категорий",
)
async def get_categories() -> list[CategoryResponse]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not Implemented"
    )


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание категории"
)
async def create_category() -> CategoryResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not Implemented"
    )