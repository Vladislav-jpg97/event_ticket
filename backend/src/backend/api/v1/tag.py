from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from backend.dependencies.tag import TagServiceDep
from backend.dependencies.user_auth import require_role, UserRole
from backend.models import User, Tag
from backend.schemas.tag import TagsResponse, TagCreate

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
)


@router.get("", response_model=list[TagsResponse], summary="Список всех тегов")
async def get_tags(service: TagServiceDep):
    return await service.get_all_tags()


@router.post(
    "/",
    response_model=TagsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание тега"
)
async def create_tag(
    body: TagCreate,
    service: TagServiceDep,
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> Tag:
    return await service.create_tag(body)