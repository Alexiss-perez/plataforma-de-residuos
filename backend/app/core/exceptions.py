from __future__ import annotations

from typing import Any


class AppException(Exception):
    code: str = "INTERNAL_ERROR"
    status_code: int = 500
    message: str = "Internal server error"

    def __init__(self, message: str | None = None, details: dict[str, Any] | None = None) -> None:
        self.message = message or self.__class__.message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    code = "NOT_FOUND"
    status_code = 404
    message = "Resource not found"


class ConflictError(AppException):
    code = "CONFLICT"
    status_code = 409
    message = "Conflict"


class BadRequestError(AppException):
    code = "BAD_REQUEST"
    status_code = 400
    message = "Bad request"


class UnauthorizedError(AppException):
    code = "UNAUTHORIZED"
    status_code = 401
    message = "Unauthorized"


class ForbiddenError(AppException):
    code = "FORBIDDEN"
    status_code = 403
    message = "Forbidden"


class ValidationError(AppException):
    code = "VALIDATION_ERROR"
    status_code = 422
    message = "Validation error"


class MaterialNotAvailableError(AppException):
    code = "MATERIAL_NOT_AVAILABLE"
    status_code = 409
    message = "Material is not available"


class NeedClosedError(AppException):
    code = "NEED_CLOSED"
    status_code = 409
    message = "Need is closed"


class IllegalTransitionError(AppException):
    code = "ILLEGAL_TRANSITION"
    status_code = 409
    message = "Illegal state transition"


class HazardousMaterialError(AppException):
    code = "HAZARDOUS_MATERIAL"
    status_code = 422
    message = "This material requires specialized handling"


class PickupNotAssignedError(AppException):
    code = "PICKUP_NOT_ASSIGNED"
    status_code = 409
    message = "Pickup has no assigned collector"
