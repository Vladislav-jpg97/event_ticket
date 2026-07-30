from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.core.security import SecurityManager
from backend.models import User
from backend.repository.user import UserRepository
from backend.schemas.auth import UserCreate


class AuthService:
    def __init__(
            self,
            session: AsyncSession,
            user_repo: UserRepository,
            security_manager: SecurityManager
    ) -> None:

        self.session = session
        self.user_repo = user_repo
        self.security_manager = security_manager

    async def register_user(self, body: UserCreate):
        existing_email, existing_username = await self.user_repo.get_by_email(
            body.email), await self.user_repo.get_by_username(body.username)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        hashed_password = self.security_manager.hash_password(body.password)
        user = User(
            email=body.email,
            username=body.username,
            hashed_password=hashed_password,
            is_verified=False,
        )
        await self.user_repo.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user