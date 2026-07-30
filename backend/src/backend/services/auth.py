from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.core.security import SecurityManager
from backend.models import User
from backend.repository.user import UserRepository
from backend.schemas.auth import UserCreate, LoginRequest


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

    async def login_user(self, body: LoginRequest, client_ip: str, redis_client):
        rate_limit_key = f"login_attempts:{client_ip}"

        # 1. Проверяем, не заблокирован ли IP (если попыток уже >= 5)
        attempts = await redis_client.get(rate_limit_key)
        if attempts and int(attempts) >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
            )

        # 2. Ищем пользователя и проверяем пароль
        user = await self.user_repo.get_by_email(body.email)

        if user is None or not self.security_manager.verify_password(
                body.password, user.hashed_password
        ):
            # Увеличиваем счетчик неудачных попыток и ставим TTL 15 минут (900 секунд)
            pipe = redis_client.pipeline()
            pipe.incr(rate_limit_key)
            pipe.expire(rate_limit_key, 900)
            await pipe.execute()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # 3. При успешном логине сбрасываем счётчик попыток в Redis
        await redis_client.delete(rate_limit_key)

        # 4. Генерируем токены
        access_token = await self.security_manager.create_access_token(user.id)
        refresh_token = await self.security_manager.create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }