from datetime import datetime

from pydantic import BaseModel


class TicketCreate(BaseModel):
    quantity: int


class EventMiniResponse(BaseModel):
    id: int
    title: str
    slug: str
    start_at: datetime
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
