from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.src.backend.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=10,
    max_overflow=20,
)

SessionDb = async_sessionmaker(  # <-- используем асинхронный фабрикатор сессий
    bind=engine,
    expire_on_commit=False,
)