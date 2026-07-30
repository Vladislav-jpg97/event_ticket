from __future__ import annotations
from datetime import datetime

from sqlalchemy import func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.enums import Role
from backend.models.base import Base


class User(Base):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[Role] = mapped_column(
        SQLEnum(Role, name="role", create_type=False),
        default=Role.ADMIN,
        nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    bio: Mapped[str] = mapped_column(default="")
    avatar_url: Mapped[str] = mapped_column(default="")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())