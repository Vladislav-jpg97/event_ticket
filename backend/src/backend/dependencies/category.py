from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies.database import SessionDep
from backend.repository.category import CategoryRepository
from backend.services.category import CategoryService


async def get_category_repo(
        session: SessionDep,
) -> CategoryRepository:
    return CategoryRepository(session)


CategoryRepoDep = Annotated[
    CategoryRepository,
    Depends(get_category_repo),
]


async def get_category_service(
        session: SessionDep,
        category_repo: CategoryRepoDep,
) -> CategoryService:
    return CategoryService(session=session, category_repo=category_repo)


CategoryServiceDep = Annotated[
    CategoryService,
    Depends(get_category_service),
]
