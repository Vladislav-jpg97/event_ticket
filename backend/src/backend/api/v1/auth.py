from fastapi import APIRouter, HTTPException, status, Request, Response, Depends
from fastapi.security import HTTPAuthorizationCredentials

from backend.core.cache import RedisDep
from backend.dependencies.auth import UserServiceDep, security_scheme
from backend.schemas.auth import (
    UserCreate,
    UserResponse,
    LoginRequest,
    Token,
    RefreshToken,
    ForgotPasswordRequest,
    ResetPasswordRequest, AccessTokenResponse, VerifyEmailRequest,
)

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
    "/login",
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
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Обновление токенов"
)
async def refresh_tokens(
        body: RefreshToken
) -> Token:
    raise HTTPException(status_code=501, detail="Not Implemented")


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
        body: ForgotPasswordRequest
):
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.post(
    "/auth/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Сброс пароля"
)
async def reset_password(
        body: ResetPasswordRequest
):
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get(
    "/users/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Профиль текущего пользователя"
)
async def get_my_profile() -> UserResponse:
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get(
    "/users/{username}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Профиль пользователя по username"
)
async def get_user_by_username(
        body: str
) -> UserResponse:
    raise HTTPException(status_code=501, detail="Not Implemented")
