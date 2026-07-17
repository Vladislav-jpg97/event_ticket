import enum
class Role(str,enum.Enum):
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