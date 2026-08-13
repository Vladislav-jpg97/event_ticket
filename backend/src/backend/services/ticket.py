from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from redis.asyncio import Redis

from backend.core.cache import CacheService
from backend.core.enums import TicketStatus
from backend.models import Ticket
from backend.repository.event import EventRepository
from backend.repository.ticket import TicketRepository

# Lua-скрипт для атомарной проверки и декремента мест в Redis
LUA_DECREMENT_SCRIPT = """
local available = tonumber(redis.call('get', KEYS[1]))
if not available then
    return -1
end
local requested = tonumber(ARGV[1])
if available >= requested then
    redis.call('decrby', KEYS[1], requested)
    return available - requested
else
    return -2
end
"""


class TicketService:
    def __init__(
            self,
            session: AsyncSession,
            ticket_repo: TicketRepository,
            event_repo: EventRepository,
            redis_client: CacheService,
    ):
        self.ticket_repo = ticket_repo
        self.session = session
        self.event_repo = event_repo
        self.redis = redis_client

    async def buy_ticket(
            self,
            slug: str,
            user_id: int,
            quantity: int
    ):
        # 1. Проверка диапазона quantity от 1 до 5
        if not (1 <= quantity <= 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be between 1 and 5"
            )

        # Получаем событие по slug
        event = await self.event_repo.get_by_slug(slug)
        if not event or event.status != "PUBLISHED":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        redis_key = f"event:{event.id}:seats"

        # Инициализируем ключ в Redis, если его там еще нет
        if not await self.redis.exists(redis_key):
            await self.redis.set(redis_key, event.available_seats)

        # 2. Выполняем атомарный Lua-скрипт
        result = await self.redis.eval(LUA_DECREMENT_SCRIPT, 1, redis_key, quantity)

        if result == -2 or result < 0:
            current_seats = await self.redis.get(redis_key) or 0
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Not enough available seats. Remaining: {int(current_seats)}"
            )

        # 3. Фиксируем цену на момент покупки
        total_price = event.price * quantity

        # 4. Создаем билет в БД со статусом PENDING (id автоинкрементируется, uuid генерируется автоматически)
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
            # При падении оплаты возвращаем места в Redis и удаляем сам объект билета
            await self.redis.incrby(redis_key, quantity)
            await self.ticket_repo.delete(ticket)
            await self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment failed"
            )

        # 6. Успешная оплата -> статус PAID
        ticket.status = TicketStatus.PAID
        await self.session.commit()
        await self.session.refresh(ticket)

        # 7. (Здесь будет запуск Celery-задачи на email)
        # send_ticket_email.delay(ticket.id, user_id)

        return ticket

    async def _mock_payment(self) -> bool:
        # Имитация платежного шлюза (всегда True для успешного теста)
        return True