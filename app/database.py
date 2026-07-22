from collections.abc import AsyncIterator
from os import getenv
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


DATABASE_URL = getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./finance.db",
)

engine = create_async_engine(DATABASE_URL, echo=False)


if engine.url.get_backend_name() == "sqlite":

    @event.listens_for(engine.sync_engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection: Any, _: Any) -> None:
        """SQLite requires foreign-key enforcement to be enabled per connection."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# expire_on_commit=False keeps loaded ORM attributes available while FastAPI
# serializes the response after a repository commits the transaction.
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Give one database session to one request and always close it afterward."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            # A failed flush/commit leaves a session unusable until rollback.
            await session.rollback()
            raise


async def dispose_engine(database_engine: AsyncEngine = engine) -> None:
    await database_engine.dispose()


SessionDep = Annotated[AsyncSession, Depends(get_session)]
