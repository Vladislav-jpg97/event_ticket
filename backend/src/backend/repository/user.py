from sqlalchemy import select

from backend.models import User
from backend.repository.base import BaseRepository
from backend.repository.mixins import (
    AddRepositoryMixin,
    DeleteRepositoryMixin,
    RetrieveRepositoryMixin,
    UpdateRepositoryMixin,
)


class UserRepository(
    BaseRepository[User],
    AddRepositoryMixin[User],
    UpdateRepositoryMixin[User],
    DeleteRepositoryMixin[User],
    RetrieveRepositoryMixin[User],
):
    model = User

    async def get_by_id(self, obj_id: int):
        result = await self.session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalars().first()