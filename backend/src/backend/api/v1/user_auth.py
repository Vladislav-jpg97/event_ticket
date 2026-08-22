from fastapi import APIRouter, HTTPException, status, Request, Response, Depends
from fastapi.security import HTTPAuthorizationCredentials

from backend.core.cache import RedisDep
from backend.dependencies.user_auth import UserServiceDep, security_scheme, get_current_user
from backend.models import User
from backend.schemas.user_auth import (
    UserCreate,
    UserResponse,
    LoginRequest,
    Token,
    RefreshToken,
    ForgotPasswordRequest,
    ResetPasswordRequest, AccessTokenResponse, VerifyEmailRequest, UserUpdate, UserPublicResponse,
)

from fastapi import File, UploadFile
router = APIRouter(tags=["Auth & Users"])


@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя"
)
async def register(
        body: UserCreate,
        service: UserServiceDep,
) -> UserResponse:
    new_user = await service.register_user(body)
    return new_user


@router.post(
    "auth/login",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Авторизация пользователя"
)
async def login(
        body: LoginRequest,
        request: Request,
        response: Response,
        auth_service: UserServiceDep,
        redis_client: RedisDep,
) -> dict:
    client_ip = request.client.host

    tokens = await auth_service.login_user(body, client_ip, redis_client)

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        samesite="lax",
        secure=False,
    )

    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer",
    }


@router.post(
    "/auth/logout",
    status_code=status.HTTP_200_OK,
    summary="Выход из системы"
)
async def logout(
        response: Response,
        auth_service: UserServiceDep,
        credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    token = credentials.credentials
    await auth_service.logout_user(token)
    response.delete_cookie(key="refresh_token")
    return {"detail": "Successfully logged out"}


@router.post(
    "/auth/refresh",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление токенов"
)
async def refresh_tokens(
        request: Request,
        auth_service: UserServiceDep,
) -> dict:
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )

    return await auth_service.refresh_access_token(refresh_token)

@router.post(
    "/auth/verify-email",
    status_code=status.HTTP_200_OK,
    summary="Подтверждение email"
)
async def verify_email(
        body: VerifyEmailRequest,
        auth_service: UserServiceDep,
):
    return await auth_service.verify_email(body.token)


@router.post(
    "/auth/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Запрос на восстановление пароля"
)
async def forgot_password(
        body: ForgotPasswordRequest,
        service: UserServiceDep,
):
    return await service.forget_password(body)


@router.post(
    "/auth/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Сброс пароля"
)
async def resset_password(
        body: ResetPasswordRequest,
        service: UserServiceDep,
):
    return await service.resset_password(body)







@router.post(
    "/users/me/avatar",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Загрузка аватара пользователя"
)
async def upload_avatar(
        service: UserServiceDep,
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),

) -> UserResponse:
    avatar_url = await service.save_user_avatar(current_user.id, file)
    updated_user = await service.update_avatar(current_user.id, avatar_url)

    return updated_user


@router.get(
    "/users/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Профиль текущего пользователя"
)
async def get_my_profile(
        current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch(
    "/users/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление пользователя"
)
async def update_profile(
        body: UserUpdate,
        service: UserServiceDep,
        current_user: User = Depends(get_current_user),

) -> UserResponse:
    user = await service.user_update(current_user.id, body)
    return UserResponse.model_validate(user)


@router.get(
    "/users/{username}",
    response_model=UserPublicResponse,
    status_code=status.HTTP_200_OK,
    summary="Профиль пользователя по username"
)
async def get_user_by_username(
        username: str,
        service: UserServiceDep,
) -> UserPublicResponse:
    return await service.get_public_profile(username)


@router.get(
    "/{username}/events",
    status_code=status.HTTP_200_OK,
    summary="Мероприятия организатора"
)
async def get_organizer_events(
        username: str,
        service: UserServiceDep,
) -> list:
    return await service.get_organizer_events(username)