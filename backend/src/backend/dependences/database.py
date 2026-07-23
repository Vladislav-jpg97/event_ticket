from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.backend.core.database import SessionDb


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionDb() as session:
        try:
            yield session
            await session.commit()
        finally:
            await session.close()
