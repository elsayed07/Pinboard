from http import HTTPStatus


class ApplicationError(Exception):
    def __init__(self, message: str, code: int = HTTPStatus.BAD_REQUEST) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(ApplicationError):
    def __init__(self, message: str = "Not found.") -> None:
        super().__init__(message, code=HTTPStatus.NOT_FOUND)


class PermissionDeniedError(ApplicationError):
    def __init__(self, message: str = "Permission denied.") -> None:
        super().__init__(message, code=HTTPStatus.FORBIDDEN)


class ConflictError(ApplicationError):
    def __init__(self, message: str = "Conflict.") -> None:
        super().__init__(message, code=HTTPStatus.CONFLICT)


class ValidationError(ApplicationError):
    def __init__(self, message: str = "Validation error.") -> None:
        super().__init__(message, code=HTTPStatus.UNPROCESSABLE_ENTITY)
