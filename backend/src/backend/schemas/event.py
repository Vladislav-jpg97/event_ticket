from datetime import datetime
from backend.schemas.category import CategoriesResponse
from pydantic import BaseModel, Field, field_validator, ConfigDict

from backend.schemas.tag import TagsResponse
from backend.schemas.user_auth import UserResponse


class EventCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    venue: str = Field(..., min_length=2)
    city: str = Field(..., min_length=2)
    starts_at: datetime
    ends_at: datetime
    capacity: int = Field(..., ge=1, le=10000)
    price: float = Field(..., ge=0)
    category_id: int
    tags: list[str] = Field(default=[], max_length=10)

    @field_validator("starts_at")
    @classmethod
    def validate_starts_at(cls, value: datetime) -> datetime:
        if value.tzinfo is not None:
            value = value.astimezone().replace(tzinfo=None)
        now = datetime.now()
        if value <= now:
            raise ValueError("starts_at должен быть в будущем")
        return value

    @field_validator("ends_at")
    @classmethod
    def validate_ends_at(cls, value: datetime, info) -> datetime:
        if value.tzinfo is not None:
            value = value.astimezone().replace(tzinfo=None)
        starts_at = info.data.get("starts_at")
        if starts_at and value <= starts_at:
            raise ValueError("ends_at должен быть позже starts_at")
        return value


class OrganizerNested(BaseModel):
    id: int
    username: str
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class EventResponse(BaseModel):
    id: int
    title: str
    slug: str
    description: str | None = None
    venue: str | None = None
    city: str | None = None
    starts_at: datetime
    ends_at: datetime
    price: int
    status: str
    capacity: int
    tickets_sold: int
    available_seats: int
    avg_rating: float | None = None
    views: int = 0
    organizer: UserResponse
    category: CategoriesResponse | None = None
    tags: list[TagsResponse] = []

    model_config = ConfigDict(from_attributes=True)

    @field_validator("tags", mode="before")
    @classmethod
    def transform_tags(cls, v: list) -> list[str]:
        if v and not isinstance(v[0], str):
            return [tag.name for tag in v if hasattr(tag, "name")]
        return v


class PaginatedEventResponse(BaseModel):
    items: list[EventResponse]
    total: int
    page: int
    pages: int