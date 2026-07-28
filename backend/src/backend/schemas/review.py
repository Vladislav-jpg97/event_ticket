from datetime import datetime

from pydantic import BaseModel, Field

from backend.schemas.auth import UserResponse


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    text: str


class ReviewResponse(BaseModel):
    id: int
    user: UserResponse
    rating: int
    text: str
    created_at: datetime
