from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies.database import SessionDep
from backend.repository.tag import TagRepository
from backend.services.tag import TagService


async def get_tag_repo(session: SessionDep) -> TagRepository:
    return TagRepository(session)

TagRepoDep = Annotated[TagRepository, Depends(get_tag_repo)]

async def get_tag_service(
        session: SessionDep,
        tag_repo: TagRepoDep,
) -> TagService:
    return TagService(session=session, repo_tag=tag_repo)

TagServiceDep = Annotated[TagService, Depends(get_tag_service)]
