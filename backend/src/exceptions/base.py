class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        status_code: int,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code

        super().__init__(message)