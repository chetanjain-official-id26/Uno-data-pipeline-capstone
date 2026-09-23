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


class DatabaseError(AppException):
    """Internal persistence-layer failure.

    Details must not be exposed to API clients.
    """

    def __init__(self) -> None:
        super().__init__(
            "A database operation failed.",
            code="DATABASE_ERROR",
            status_code=500,
        )

class DiscoveryError(AppException):
    """Base exception for source metadata discovery."""

    def __init__(
        self,
        message: str = "Unable to discover source metadata.",
    ) -> None:
        super().__init__(
            message,
            code="DISCOVERY_ERROR",
            status_code=400,
        )


class DatabaseDiscoveryError(DiscoveryError):
    def __init__(self) -> None:
        super().__init__("Unable to retrieve databases from the source.")


class SchemaDiscoveryError(DiscoveryError):
    def __init__(self) -> None:
        super().__init__("Unable to retrieve schemas from the source.")


class TableDiscoveryError(DiscoveryError):
    def __init__(self) -> None:
        super().__init__("Unable to retrieve tables from the source.")


class ColumnDiscoveryError(DiscoveryError):
    def __init__(self) -> None:
        super().__init__("Unable to retrieve columns from the source.")