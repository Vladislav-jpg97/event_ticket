from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from backend.models import Category
from backend.repository.category import CategoryRepository
from backend.schemas.category import CategoryCreate, CategoriesResponse


class CategoryService:
    def __init__(self, session: AsyncSession, category_repo: CategoryRepository):
        self.session = session
        self.category_repo = category_repo

    async def get_all_categories(self) -> list[CategoriesResponse]:
        categories = await self.category_repo.get_all()
        # Превращаем модели SQLAlchemy в Pydantic схемы
        return [CategoriesResponse.model_validate(cat) for cat in categories]

    async def create_category(self, data: CategoryCreate) -> CategoriesResponse:
        category = Category(name=data.name, slug=data.slug)
        try:
            await self.category_repo.add(category)
            await self.session.commit()
            await self.session.refresh(category)
            return CategoriesResponse.model_validate(category)
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category with this name or slug already exists."
            )