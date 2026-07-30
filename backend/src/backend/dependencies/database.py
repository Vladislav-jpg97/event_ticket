from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import SessionFactory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with SessionFactory() as session:
            yield session
    finally:
        await session.close()


SessionDep = Annotated[
    AsyncSession,
    Depends(get_db),
]
