from typing import Annotated

from fastapi import Depends
from backend.core.security import SecurityManager
from backend.dependencies.database import SessionDep
from backend.repository.user import UserRepository
from backend.services.auth import AuthService


async def get_user_repo(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepoDep = Annotated[
    UserRepository,
    Depends(get_user_repo),
]


async def get_user_service(
        user_repo: UserRepoDep,
        session: SessionDep,
        security_manager: SecurityManager = Depends(SecurityManager),

) -> AuthService:
    return AuthService(session=session, user_repo=user_repo, security_manager=security_manager)


UserServiceDep = Annotated[
    AuthService,
    Depends(get_user_service),
]
