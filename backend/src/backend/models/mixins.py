from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class IdentityMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

