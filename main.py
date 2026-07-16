from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from app.routers.transactions import router as transactions_router
from app.database import create_tables, dispose_engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await create_tables()

    try:
        yield
    finally:
        await dispose_engine()

def create_app() -> FastAPI:
    application = FastAPI(
        title="Finance Tracker API",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.include_router(transactions_router)
    return application


app = create_app()

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Verify that the application process is running."""
    return {"status": "healthy"}

