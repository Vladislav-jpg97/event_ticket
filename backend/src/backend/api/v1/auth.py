from fastapi import APIRouter, HTTPException, status
from backend.schemas.auth import (
    UserCreate,
    UserResponse,
    LoginRequest,
    Token,
    RefreshToken,
    VerifyEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

router = APIRouter(prefix="/api/v1", tags=["Auth & Users"])


@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя"
)
async def register(
        request: UserCreate
) -> UserResponse:
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.post(
    "/auth/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Вход в систему"
)
async def login(
        request: LoginRequest
) -> Token:
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход из системы"
)
async def logout():
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.post(
    "/auth/refresh",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Обновление токенов"
)
async def refresh_tokens(
        request: RefreshToken
) -> Token:
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.post(
    "/auth/verify-email",
    status_code=status.HTTP_200_OK,
    summary="Подтверждение email"
)
async def verify_email(
        request: VerifyEmailRequest
):
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.post(
    "/auth/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Запрос на восстановление пароля"
)
async def forgot_password(
        request: ForgotPasswordRequest
):
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.post(
    "/auth/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Сброс пароля"
)
async def reset_password(
        request: ResetPasswordRequest
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
        username: str
) -> UserResponse:
    raise HTTPException(status_code=501, detail="Not Implemented")
