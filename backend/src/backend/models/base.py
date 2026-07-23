from sqlalchemy.orm import DeclarativeBase

from backend.models.mixins import IdentityMixin


class Base(IdentityMixin,DeclarativeBase):
    pass

