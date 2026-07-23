from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import dispose_engine
from app.errors.exception_handlers import register_exception_handlers
from app.middlewares.request_logging import register_request_logging
from app.routers.categories import router as categories_router
from app.routers.transactions import router as transactions_router
from app.routers.users import router as users_router


async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Alembic owns schema creation; app startup only manages runtime resources.
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
    register_request_logging(application)
    register_exception_handlers(application)
    application.add_api_route("/health", health_check, methods=["GET"], tags=["system"])
    application.include_router(users_router)
    application.include_router(categories_router)
    application.include_router(transactions_router)
    return application


app = create_app()
