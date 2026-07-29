from fastapi import APIRouter, HTTPException
from starlette import status
from backend.schemas.category import CategoriesResponse

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@router.get(
    "/",
    response_model=list[CategoriesResponse],
    status_code=status.HTTP_200_OK,
    summary="Получение всех категорий",
)
async def get_categories() -> list[CategoriesResponse]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not Implemented"
    )


@router.post(
    "/",
    response_model=CategoriesResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание категории"
)
async def create_category() -> CategoriesResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not Implemented"
    )