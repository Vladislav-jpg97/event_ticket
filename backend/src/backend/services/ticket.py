from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.cache import CacheService
from backend.core.enums import TicketStatus
from backend.models import Ticket
from backend.repository.event import EventRepository
from backend.repository.ticket import TicketRepository

# Lua-скрипт для атомарной проверки и декремента мест в Redis
LUA_DECREMENT_SCRIPT = """
local current = tonumber(redis.call('get', KEYS[1]))
if current == nil then
    return -2
end
local quantity = tonumber(ARGV[1])
if current >= quantity then
    return redis.call('decrby', KEYS[1], quantity)
else
    return -1
end
"""


class TicketService:
    def __init__(
            self,
            session: AsyncSession,
            ticket_repo = TicketRepository,
            event_repo = EventRepository,
            redis_client = CacheService
    ):
        self.session = session
        self.ticket_repo = ticket_repo
        self.event_repo = event_repo
        self.redis = redis_client  # Это твой CacheService

    async def _mock_payment(self) -> bool:
        """Имитация платежного шлюза (всегда True для успешного теста)."""
        return True

    async def buy_ticket(
            self,
            slug: str,
            user_id: int,
            quantity: int
    ) -> dict:
        # 1. Проверка диапазона quantity от 1 до 5
        if not (1 <= quantity <= 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be between 1 and 5"
            )

        # Получаем событие по slug (проверяем, что оно опубликовано)
        event = await self.event_repo.get_by_slug(slug)
        if not event or event.status != "PUBLISHED":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        # Берем чистый redis-клиент из CacheService для сырых атомарных операций
        raw_redis = self.redis.client
        redis_key = f"event:{event.id}:seats"

        # Инициализируем ключ в Redis, если его там еще нет
        if not await raw_redis.exists(redis_key):
            await raw_redis.set(redis_key, event.available_seats)

        # 2. Выполняем атомарный Lua-скрипт (защита от race condition)
        result = await raw_redis.eval(LUA_DECREMENT_SCRIPT, 1, redis_key, quantity)

        if result == -2 or result < 0:
            current_seats = await raw_redis.get(redis_key) or 0
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Not enough available seats. Remaining: {int(current_seats)}"
            )

        # 3. Фиксируем цену на момент покупки
        total_price = event.price * quantity

        # 4. Создаем билет в БД со статусом PENDING
        ticket = Ticket(
            event_id=event.id,
            buyer_id=user_id,
            quantity=quantity,
            total_price=total_price,
            status=TicketStatus.PENDING
        )
        await self.ticket_repo.add(ticket)
        await self.session.commit()
        await self.session.refresh(ticket)

        # 5. Mock оплата
        payment_success = await self._mock_payment()

        if not payment_success:
            # При падении оплаты возвращаем места обратно в Redis и удаляем билет
            await raw_redis.incrby(redis_key, quantity)
            await self.ticket_repo.delete(ticket)
            await self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment failed"
            )

        # 6. Успешная оплата -> переводим статус в PAID
        ticket.status = TicketStatus.PAID
        await self.session.commit()
        await self.session.refresh(ticket)

        # 7. Формируем словарь для валидации через Pydantic-схему TicketResponse
        event_mini = {
            "id": event.id,
            "title": event.title,
            "slug": event.slug,
            "start_at": getattr(event, "start_at", getattr(event, "starts_at", None)),
            "venue": event.venue,
            "city": event.city,
        }

        # Безопасно извлекаем дату создания (если атрибута нет, подставляем текущую)
        created_at = (
                getattr(ticket, "created_at", None)
                or getattr(ticket, "created_on", None)
                or datetime.utcnow()
        )

        return {
            "id": ticket.id,
            "uuid": str(ticket.uuid),
            "event": event_mini,
            "quantity": ticket.quantity,
            "total_price": float(ticket.total_price),
            "status": ticket.status.value if hasattr(ticket.status, "value") else ticket.status,
            "created_at": created_at,
        }

    async def _mock_payment(self) -> bool:
        return True

    async def cancel_ticket(self, ticket_id: int, user_id: int):
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        if ticket.buyer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only cancel your own tickets"
            )

        if ticket.status != TicketStatus.PAID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only paid tickets can be cancelled"
            )
        event = await self.event_repo.get_by_id(ticket.event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        time_now = datetime.now(timezone.utc)
        event_time = event.starts_at.replace(tzinfo=timezone.utc)
        if event_time - time_now < timedelta(hours=2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="It's too late to cancel"
            )
        quantity_redis =await self.redis.incr(f"event:seats:{event.id}", amount=ticket.quantity)
        ticket.status = TicketStatus.CANCELED
        await self.session.commit()
        await self.session.refresh(ticket)

