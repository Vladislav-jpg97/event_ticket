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
