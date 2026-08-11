from fastapi import APIRouter, Depends
from starlette import status

from backend.dependencies.category import CategoryServiceDep
from backend.dependencies.user_auth import require_role, UserRole
from backend.models import User
from backend.schemas.category import CategoriesResponse, CategoryCreate

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
async def get_categories(service: CategoryServiceDep):
    # Убрали аннотацию -> list[...] у функции, чтобы FastAPI не путался
    return await service.get_all_categories()


@router.post(
    "/",
    response_model=CategoriesResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание категории"
)
async def create_category(
        body: CategoryCreate,
        service: CategoryServiceDep,
        current_user: User = Depends(require_role(UserRole.ADMIN))
):
    # Убрали аннотацию -> Category у функции
    return await service.create_category(body)