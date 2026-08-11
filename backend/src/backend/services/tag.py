from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Tag
from backend.repository.tag import TagRepository
from backend.schemas.tag import TagCreate


class TagService:
    def __init__(self, session: AsyncSession, repo_tag: TagRepository):
        self.session = session
        self.repo_tag = repo_tag

    async def get_all_tags(self) -> list[Tag]:
        return await self.repo_tag.get_all()

    async def create_tag(self, data: TagCreate) -> Tag:
        tag = Tag(name=data.name)
        try:
            await self.repo_tag.add(tag)
            await self.session.commit()
            await self.session.refresh(tag)
            return tag
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tag with this name or slug already exists."
            )