import enum

class Role(str, enum.Enum):
    ATTENDEE = 'ATTENDEE'
    ORGANIZER = 'ORGANIZER'
    ADMIN = 'ADMIN'

class EventStatus(str, enum.Enum):
    DRAFT = 'DRAFT'
    PUBLISHED = 'PUBLISHED'
    CANCELED = 'CANCELED'
    COMPLETED = 'COMPLETED'

class TicketStatus(str, enum.Enum):
    PENDING = 'PENDING'
    PAID = 'PAID'
    CANCELED = 'CANCELED'


class EventSortEnum(str, enum.Enum):
    DATE_ASC = "date_asc"
    PRICE_DESC = "price_desc"
    RATING = "rating"
    POPULAR = "popular"