class ApplicationError(Exception):
    """Base class for expected errors raised by application code."""

    code = "application_error"

    def __init__(self, message: str, *, context: dict[str, str] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}


class ResourceNotFoundError(ApplicationError):
    """Raised when an entity requested by its identifier does not exist."""

    code = "resource_not_found"

    def __init__(self, resource: str, resource_id: object) -> None:
        super().__init__(
            f"{resource} not found",
            context={
                "resource": resource,
                "resource_id": str(resource_id),
            },
        )


class DuplicateResourceError(ApplicationError):
    """Raised when a uniqueness rule prevents creating or updating an entity."""

    code = "duplicate_resource"

    def __init__(self, resource: str, message: str) -> None:
        super().__init__(message, context={"resource": resource})


class ResourceInUseError(ApplicationError):
    """Raised when related data prevents changing or deleting an entity."""

    code = "resource_in_use"

    def __init__(self, resource: str, resource_id: object, message: str) -> None:
        super().__init__(
            message,
            context={
                "resource": resource,
                "resource_id": str(resource_id),
            },
        )


class BusinessRuleViolationError(ApplicationError):
    """Raised when valid input violates a domain rule."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
