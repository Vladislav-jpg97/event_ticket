from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    quantity: int


class EventMiniResponse(BaseModel):
    id: int
    title: str
    slug: str
    starts_at: datetime
    venue: str
    city: str


class TicketResponse(BaseModel):
    id: int
    uuid: str
    event: EventMiniResponse
    quantity: int
    total_price: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
