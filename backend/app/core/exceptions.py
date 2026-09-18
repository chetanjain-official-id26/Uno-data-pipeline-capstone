class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        status_code: int = 500,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code

        super().__init__(message)


class ConnectionNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Connection was not found.",
            code="CONNECTION_NOT_FOUND",
            status_code=404,
        )


class ConnectionEncryptionError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Unable to process connection credentials.",
            code="CONNECTION_ENCRYPTION_ERROR",
            status_code=500,
        )


class ConnectionTestError(AppException):
    def __init__(
        self,
        message: str,
        *,
        code: str = "CONNECTION_TEST_FAILED",
    ) -> None:
        super().__init__(
            message,
            code=code,
            status_code=400,
        )