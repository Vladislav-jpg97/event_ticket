from sqlalchemy import select
from backend.models import Tag
from backend.repository.base import BaseRepository
from backend.repository.mixins import (
    AddRepositoryMixin,
    DeleteRepositoryMixin,
    RetrieveRepositoryMixin,
    UpdateRepositoryMixin,
)


class TagRepository(
    BaseRepository[Tag],
    AddRepositoryMixin[Tag],
    UpdateRepositoryMixin[Tag],
    DeleteRepositoryMixin[Tag],
    RetrieveRepositoryMixin[Tag],
):
    model = Tag

    async def get_all(self) -> list[Tag]:
        stmt = select(self.model)
        results = await self.session.execute(stmt)
        return list(results.scalars().all())