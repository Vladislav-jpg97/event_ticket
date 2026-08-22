import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select
from backend.core.enums import EventStatus

from backend.models.category import Category
from backend.models.event import Event
from backend.models.user import User


async def seed_database():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("❌ DATABASE_URL не найдена!")

    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("🌱 Запуск сидера...")

        try:
            # 1. Проверяем организатора
            result = await session.execute(select(User).limit(1))
            existing_user = result.scalars().first()

            if not existing_user:
                print("❌ Ошибка: В базе нет пользователей! Сначала зарегистрируйте пользователя через API.")
                return

            # 2. Проверяем или создаем категорию "Технологии"
            cat_result = await session.execute(select(Category).where(Category.slug == "tech"))
            cat_tech = cat_result.scalars().first()

            if not cat_tech:
                cat_tech = Category(name="Технологии", slug="tech")
                session.add(cat_tech)
                await session.flush()
                print("📂 Категория 'Технологии' создана.")
            else:
                print("📂 Категория 'Технологии' уже существует.")

            # 3. Проверяем или создаем тестовое событие
            event_result = await session.execute(select(Event).where(Event.slug == "python-backend-meetup-2026"))
            event1 = event_result.scalars().first()

            if not event1:
                event1 = Event(
                    title="Python Backend Meetup 2026",
                    slug="python-backend-meetup-2026",
                    description="Масштабная встреча разработчиков, обсуждаем FastAPI, асинхронность и архитектуру.",
                    venue="IT Park Conference Hall",
                    city="Ташкент",
                    starts_at=datetime.now() + timedelta(days=10),
                    ends_at=datetime.now() + timedelta(days=10, hours=4),
                    capacity=100,
                    available_seats=100,
                    price=Decimal("150.00"),
                    status=EventStatus.PUBLISHED,
                    category_id=cat_tech.id,
                    organizer_id=existing_user.id
                )
                session.add(event1)
                await session.commit()
                print(f"✅ Создано новое событие с ID: {event1.id}")
            else:
                print(f"ℹ️ Событие с таким slug уже существует (ID: {event1.id}). Пропускаем создание.")

        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при сидировании: {e}")
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())