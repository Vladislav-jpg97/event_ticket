from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from fastapi import HTTPException,UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.core.cache import CacheService
from backend.core.security import SecurityManager
from backend.models import User
from backend.repository.user_auth import UserRepository
from backend.schemas.user_auth import UserCreate, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, UserUpdate

import uuid
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

class AuthService:
    def __init__(
            self,
            session: AsyncSession,
            user_repo: UserRepository,
            security_manager: SecurityManager,
            cache_service: CacheService,
    ) -> None:

        self.session = session
        self.user_repo = user_repo
        self.security_manager = security_manager
        self.cache_service = cache_service

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

        verification_token = str(uuid.uuid4())

        await self.cache_service.set(
            key=f"verify:{verification_token}",
            value=user.id,
            ttl=86400
        )
        print(f"DEBUG: Verification Token for {user.email} -> {verification_token}")

        return user

    async def login_user(self, body: LoginRequest, client_ip: str, redis_client):
        rate_limit_key = f"login_attempts:{client_ip}"

        attempts = await redis_client.get(rate_limit_key)
        if attempts and int(attempts) >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
            )

        user = await self.user_repo.get_by_email(body.email)

        if user is None or not self.security_manager.verify_password(
                body.password, user.hashed_password
        ):
            pipe = redis_client.pipeline()
            pipe.incr(rate_limit_key)
            pipe.expire(rate_limit_key, 900)
            await pipe.execute()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        await redis_client.delete(rate_limit_key)

        access_token = await self.security_manager.create_access_token(user.id)
        refresh_token = await self.security_manager.create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def logout_user(self, token: str):
        payload = await self.security_manager.get_token_payload(token)
        jti = payload.get("jti")
        exp = payload.get("exp")

        if jti and exp:
            current_timestamp = int(datetime.now(timezone.utc).timestamp())
            ttl = exp - current_timestamp

            if ttl > 0:
                await self.cache_service.add_to_blacklist(jti=jti, ttl=ttl)

    async def refresh_access_token(self, token: str | None):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        if not token:
            raise credentials_exception

        payload = await self.security_manager.get_token_payload(token)
        jti = payload.get("jti")
        token_type = payload.get("token_type")
        user_id = payload.get("sub")

        if token_type != "refresh_token" or not user_id:
            raise credentials_exception

        if jti:
            is_blacklisted = await self.cache_service.client.get("is_blacklisted")
            if is_blacklisted:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                )
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        access_token = await self.security_manager.create_access_token(user.id)
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    async def verify_email(self, token: str):

        print(f"DEBUG: Trying to verify token -> {token}")
        cache_key = f"verify:{token}"
        payload = await self.cache_service.get(cache_key)
        print(f"DEBUG: Payload from Redis -> {payload}")

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )
        user_id = int(payload)

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )
        user.is_verified = True
        await self.cache_service.delete(f"verify:{token}")
        await self.session.commit()
        await self.session.refresh(user)
        return {"message": "Email successfully verified"}

    async def forget_password(self, body: ForgotPasswordRequest):
        user = await self.user_repo.get_by_email(body.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )
        reset_token =  str(uuid.uuid4())
        await self.cache_service.set(
            key=f"reset:{reset_token}",
            value=user.email,
            ttl=3600
        )
        await self.session.commit()
        await self.session.refresh(user)
        print(f"DEBUG: Forget password -> {reset_token}")

    async def resset_password(self, body: ResetPasswordRequest):
        cache_key = f"reset:{body.token}"
        email = await self.cache_service.get(cache_key)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",

            )

        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )

        new_hashed_password = self.security_manager.hash_password(body.new_password)
        user.hashed_password = new_hashed_password
        await self.cache_service.delete(cache_key)
        await self.session.commit()
        await self.session.refresh(user)
        return {"message": "Password successfully changed"}

    async def user_update(self, user_id: int, body: UserUpdate) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = body.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        await self.user_repo.update(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user


    async def get_public_profile(self, username: str):
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def save_user_avatar(self, user_id: int, file: UploadFile) -> str:
        # 1. Проверяем тип файла
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Allowed types: image/jpeg, image/png, image/webp",
            )

        # 2. Читаем контент и проверяем размер (до 5 МБ)
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds the 5 MB limit",
            )

        # 3. Генерируем уникальное имя файла по ТЗ
        suffix = Path(file.filename).suffix.lower() if file.filename else ".jpg"
        unique_filename = f"{user_id}_{uuid4().hex[:8]}{suffix}"

        upload_dir = Path("static/avatars")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / unique_filename

        # 4. Записываем файл на диск
        with open(file_path, "wb") as f:
            f.write(content)

        # 5. Возвращаем относительный URL
        return f"/static/avatars/{unique_filename}"

    async def update_avatar(self, user_id: int, avatar_url: str) -> User:
        # 1. Получаем пользователя
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # 2. Обновляем поле аватара
        user.avatar_url = avatar_url

        # 3. Сохраняем в базе
        await self.user_repo.update(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user