from sqlalchemy import Select

from backend.core.enums import EventSortEnum
from backend.models import Event
from backend.models.category import Category
from backend.models.tag import Tag




def apply_event_filters(stmt: Select, filters) -> Select:
    """Применяет фильтры из Pydantic-схемы к объекту запроса SQLAlchemy"""
    if filters.q:
        stmt = stmt.where(Event.title.ilike(f"%{filters.q}%"))
    if filters.category:
        stmt = stmt.where(Event.category.has(Category.slug == filters.category))
    if filters.tag:
        stmt = stmt.where(Event.tags.any(Tag.name == filters.tag))
    if filters.city:
        stmt = stmt.where(Event.city.ilike(f"%{filters.city}%"))
    if filters.date_from:
        stmt = stmt.where(Event.starts_at >= filters.date_from)
    if filters.date_to:
        stmt = stmt.where(Event.starts_at <= filters.date_to)
    if filters.price_min is not None:
        stmt = stmt.where(Event.price >= filters.price_min)
    if filters.price_max is not None:
        stmt = stmt.where(Event.price <= filters.price_max)
    return stmt


def apply_event_sorting(stmt: Select, sort: EventSortEnum) -> Select:
    """Применяет сортировку к объекту запроса SQLAlchemy"""
    if sort == EventSortEnum.PRICE_DESC:
        return stmt.order_by(Event.price.desc())
    elif sort == EventSortEnum.RATING:
        return stmt.order_by(Event.avg_rating.desc().nulls_last())
    elif sort == EventSortEnum.POPULAR:
        return stmt.order_by(Event.views.desc())

    return stmt.order_by(Event.starts_at.asc())