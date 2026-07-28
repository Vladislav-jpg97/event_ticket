from datetime import datetime

from pydantic import BaseModel

from backend.schemas.category import CategoriesResponse


class EventCreate(BaseModel):
    title: str
    description: str
    start_at: datetime
    capacity: int
    rating: int
    venue: str
    city: str
    price: float
    category_id: int
    tags: list[str] = []


class OrganizerNested(BaseModel):
    id: int
    username: str
    avatar_url: str


class EventResponse(BaseModel):
    id: int
    title: str
    slug: str
    city: str
    start_at: datetime
    price: float
    status: str
    available_seats: int
    avg_rating: float
    view: int
    organizer: OrganizerNested
    category: CategoriesResponse
    tags: list[str]


class PaginatedEventResponse(BaseModel):
    items: list[EventResponse]
    total: int
    page: int
    pages: int
