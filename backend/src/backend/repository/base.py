from typing import TypeVar, Type, Generic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

M = TypeVar("M")


class BaseRepository(Generic[M]):
    model: Type[M]

    def __init__(self, session: AsyncSession):
        self.session = session

    @property
    def base_query(self):
        return select(self.model)