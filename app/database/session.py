import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

# connect args for asyncpg
# full list can be found here: https://magicstack.github.io/asyncpg/current/api/index.html#connection
connect_args = {"command_timeout": settings.app_settings.query_timeout_seconds}

engine = create_async_engine(
    settings.core_postgres_settings.async_uri.geturl(),
    future=True,
    echo=settings.app_settings.debug_query,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False, expire_on_commit=False, class_=AsyncSession
)
SessionLocal.configure(bind=engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
