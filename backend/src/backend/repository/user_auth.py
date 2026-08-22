from sqlalchemy import select

from backend.models import User, Event
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

    async def get_events_by_user_id(
            self
    , user_id: int
    ):
        stmt = select(Event).where(Event.organizer_id == user_id)
        res = await self.session.execute(stmt)
        return res.scalars().all()