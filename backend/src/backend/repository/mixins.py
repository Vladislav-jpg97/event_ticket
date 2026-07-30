from typing import Generic
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repository.base import M


class AddRepositoryMixin(Generic[M]):
    model: M
    session: AsyncSession

    async def add(self, obj: M) -> M:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj


class UpdateRepositoryMixin(Generic[M]):
    model: M
    session: AsyncSession

    async def update(self, obj: M) -> M:
        await self.session.merge(obj)
        await self.session.flush()


class DeleteRepositoryMixin(Generic[M]):
    model: M
    session: AsyncSession

    async def delete(self, obj: M) -> M:
        await self.session.delete(obj)
        await self.session.flush()


class RetrieveRepositoryMixin(Generic[M]):
    model: M
    session: AsyncSession
    base_query: Select

    async def get_by_id(self, obj_id: int | UUID) -> M | None:
        stmt = self.base_query.where(self.model.id == obj_id)
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        return obj

    async def get_by_email(self, email: str) -> M | None:
        return (
            await self.session.execute(
                select(
                    self.model.email == email
                )
            )
        ).scalar_one_or_none()

    async def get_by_username(self, username: str) -> M | None:
        return (
            await self.session.execute(
                select(
                    self.model.username == username
                )
            )
        ).scalar_one_or_none()
