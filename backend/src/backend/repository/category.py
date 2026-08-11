from sqlalchemy import select

from backend.models import Category
from backend.repository.base import BaseRepository
from backend.repository.mixins import (
    AddRepositoryMixin,
    DeleteRepositoryMixin,
    RetrieveRepositoryMixin,
    UpdateRepositoryMixin,
)


class CategoryRepository(
    BaseRepository[Category],
    AddRepositoryMixin[Category],
    UpdateRepositoryMixin[Category],
    DeleteRepositoryMixin[Category],
    RetrieveRepositoryMixin[Category],
):
    model = Category
    async def get_all(self) -> list[Category]:
        stmt = select(self.model)
        results = await self.session.execute(stmt)
        return list(results.scalars().all())


