from sqlalchemy.orm import Mapped, mapped_column

from backend.src.backend.core.enums import Role
from backend.src.backend.models.base import Base


class User(Base):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, index=True, not_null=True)
    hashed_password: Mapped[str] = mapped_column(not_null=True)
    role: Mapped[Role] = mapped_column(default=Role.ADMIN)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    bio: Mapped[str] = mapped_column(default="")
    avatar_url: Mapped[str] = mapped_column(default="")
