from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: str = Field(default="user")

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: str
    is_verified: bool
    created_at: datetime
    bio : str
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    bio: str | None

class UserPublicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: str
    is_verified: bool
    created_at: datetime
    bio : str






class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshToken(BaseModel):
    refresh_token: str

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Token(RefreshToken):
    access_token: str
    token_type: str

# для востановления пароля
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token : str
    new_password: str

class VerifyEmailRequest(BaseModel):
    token : str
