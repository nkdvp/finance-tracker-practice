import logging
from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import RequestResponseEndpoint


# Uvicorn already configures this logger when the server starts. Reusing it keeps
# application logs and server logs in the same output without adding another handler.
logger = logging.getLogger("uvicorn.error")

SENSITIVE_PARAMETER_NAMES = frozenset(
    {
        "api_key",
        "authorization",
        "email",
        "password",
        "access_token",
        "refresh_token",
        "token",
    }
)


def safe_query_params(request: Request) -> list[tuple[str, str]]:
    """Return query parameters while hiding values that may contain credentials."""
    return [
        (name, "***" if name.lower() in SENSITIVE_PARAMETER_NAMES else value)
        for name, value in request.query_params.multi_items()
    ]


def client_ip(request: Request) -> str:
    """A client address is optional in the ASGI request scope."""
    return request.client.host if request.client is not None else "unknown"


def register_request_logging(application: FastAPI) -> None:
    """Register one access-summary log for every HTTP request."""

    @application.middleware("http")
    async def request_logging_middleware(
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = str(uuid4())
        request_at = datetime.now(UTC).isoformat()
        started_at = perf_counter()

        # Other layers can read this value later from request.state if needed.
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (perf_counter() - started_at) * 1000
            # logger.exception includes the traceback and then the exception is
            # re-raised so FastAPI/Uvicorn can keep their normal error behavior.
            logger.exception(
                (
                    "request failed request_id=%s request_at=%s method=%s path=%s "
                    "path_params=%s query_params=%s status_code=500 "
                    "duration_ms=%.2f client_ip=%s"
                ),
                request_id,
                request_at,
                request.method,
                request.url.path,
                request.path_params,
                safe_query_params(request),
                duration_ms,
                client_ip(request),
            )
            raise

        duration_ms = (perf_counter() - started_at) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            (
                "request completed request_id=%s request_at=%s method=%s path=%s "
                "path_params=%s query_params=%s status_code=%s "
                "duration_ms=%.2f client_ip=%s"
            ),
            request_id,
            request_at,
            request.method,
            request.url.path,
            request.path_params,
            safe_query_params(request),
            response.status_code,
            duration_ms,
            client_ip(request),
        )

        return response
