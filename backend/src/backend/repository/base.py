from typing import TypeVar, Type, Generic

from sqlalchemy.ext.asyncio import AsyncSession

M = TypeVar("M")


class BaseRepository(Generic[M]):
    model: Type[M]

    def __init__(self, session: AsyncSession):
        self.session = session
