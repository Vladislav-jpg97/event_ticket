from fastapi import APIRouter, HTTPException
from starlette import status

from backend.schemas.tag import TagsResponse

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
)


@router.get(
    "/",
    response_model=list[TagsResponse],
    status_code=status.HTTP_200_OK,
    summary="Получение списка всех доступных тегов"
)
async def get_all_tags() -> list[TagsResponse]:
    raise HTTPException(status_code=501, detail="Not Implemented")