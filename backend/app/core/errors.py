class AppError(Exception):
    """Base class for all business/application errors.
    Every service raises this (never a raw HTTPException) so the global
    handler can translate it into the single standard error envelope."""

    status_code: int = 400
    code: str = "APP_ERROR"

    def __init__(self, message: str, details: dict | None = None, code: str | None = None,
                 status_code: int | None = None):
        self.message = message
        self.details = details or {}
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class ValidationAppError(AppError):
    status_code = 422
    code = "VALIDATION_ERROR"


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"


class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"


class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"
