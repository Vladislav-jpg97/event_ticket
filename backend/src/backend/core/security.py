import uuid
from datetime import datetime, timezone, timedelta

from jose import JWTError, jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from starlette import status

from backend.core.config import settings


class SecurityManager:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token = settings.access_token_expire_minutes
        self.refresh_token = settings.refresh_token_expire_days

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_access_token(self, user_id: int) -> str:
        expire = datetime.now(tz=timezone.utc) + timedelta(
            minutes=self.access_token
        )
        payload = {
            "jti": str(uuid.uuid4()),
            "sub": str(user_id),
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(
            payload, self.secret_key, algorithm=self.algorithm
        )

    async def create_refresh_token(self, user_id: int) -> str:
        expire = datetime.now(tz=timezone.utc) + timedelta(
            days=self.refresh_token
        )
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh_token",
        }
        return jwt.encode(
            payload, self.secret_key, algorithm=self.algorithm
        )

    async def decode_token(self, token: str, expected: str = "access") -> int:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id_str: str | None = payload.get("sub")
            token_type: str | None = payload.get("type")
            if user_id_str is None or token_type != expected:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        return int(user_id_str)

    async def get_token_payload(self, token: str) -> dict:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise credentials_exception
