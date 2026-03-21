import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    session = async_session()
    try:
        yield session
    finally:
        await session.close()


async def init_db():
    from app.database.models import User, ResearchSession, ResearchQuery, ResearchCache  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")
