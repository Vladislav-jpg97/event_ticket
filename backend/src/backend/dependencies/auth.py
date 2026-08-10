from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status

from backend.core.cache import CacheServiceDep, get_cache_service
from backend.core.security import SecurityManager
from backend.dependencies.database import SessionDep
from backend.models import User
from backend.repository.user import UserRepository
from backend.services.auth import AuthService

import enum

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    ORGANIZER = "ORGANIZER"
    ATTENDEE = "ATTENDEE"

async def get_user_repo(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepoDep = Annotated[
    UserRepository,
    Depends(get_user_repo),
]


async def get_user_service(
        user_repo: UserRepoDep,
        session: SessionDep,
        cache_service: CacheServiceDep,
        security_manager: SecurityManager = Depends(SecurityManager),

) -> AuthService:
    return AuthService(
        session=session,
        user_repo=user_repo,
        security_manager=security_manager,
        cache_service=cache_service
    )


UserServiceDep = Annotated[
    AuthService,
    Depends(get_user_service),
]

security_scheme = HTTPBearer()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
        security_manager: SecurityManager = Depends(SecurityManager),
        cache_service: CacheServiceDep = Depends(get_cache_service),
        user_repo: UserRepoDep = Depends(get_user_repo),
):
    token = credentials.credentials
    payload = await security_manager.get_token_payload(token)
    jti = payload.get("jti")
    user_id = payload.get("sub")

    if jti:
        is_blacklisted = await cache_service.client.exists(f"blacklist:{jti}")
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


async def require_verified(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email is not verified",
        )
    return current_user


def require_role(*roles: UserRole):
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for this role",
            )
        return current_user
    return role_checker