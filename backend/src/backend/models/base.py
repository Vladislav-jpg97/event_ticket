from sqlalchemy.orm import DeclarativeBase

from backend.src.backend.models.mixins import IdentityMixin


class Base(IdentityMixin,DeclarativeBase):
    pass

