from typing import cast

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.types import ExceptionHandler

from app.errors.custom_exceptions import (
    ApplicationError,
    BusinessRuleViolationError,
    DuplicateResourceError,
    ResourceInUseError,
    ResourceNotFoundError,
)


def error_content(exc: ApplicationError) -> dict[str, object]:
    """Keep every expected application error response in one stable shape."""
    return {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "context": exc.context,
        }
    }


async def resource_not_found_handler(
    _: Request,
    exc: ResourceNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error_content(exc),
    )


async def duplicate_resource_handler(
    _: Request,
    exc: DuplicateResourceError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_content(exc),
    )


async def resource_in_use_handler(
    _: Request,
    exc: ResourceInUseError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_content(exc),
    )


async def business_rule_violation_handler(
    _: Request,
    exc: BusinessRuleViolationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_content(exc),
    )


def register_exception_handlers(application: FastAPI) -> None:
    """Attach application-error-to-HTTP mappings to an app-factory instance."""
    application.add_exception_handler(
        ResourceNotFoundError,
        cast(ExceptionHandler, resource_not_found_handler),
    )
    application.add_exception_handler(
        DuplicateResourceError,
        cast(ExceptionHandler, duplicate_resource_handler),
    )
    application.add_exception_handler(
        ResourceInUseError,
        cast(ExceptionHandler, resource_in_use_handler),
    )
    application.add_exception_handler(
        BusinessRuleViolationError,
        cast(ExceptionHandler, business_rule_violation_handler),
    )
