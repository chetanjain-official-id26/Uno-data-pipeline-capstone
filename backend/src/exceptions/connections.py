from src.exceptions.base import AppException


class ConnectionNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "The requested connection was not found.",
            code="CONNECTION_NOT_FOUND",
            status_code=404,
        )


class ConnectionAlreadyExistsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "A connection with the same configuration already exists.",
            code="CONNECTION_ALREADY_EXISTS",
            status_code=409,
        )


class ConnectionValidationError(AppException):
    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(
            message,
            code="CONNECTION_VALIDATION_ERROR",
            status_code=400,
        )


class ConnectionEncryptionError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Unable to securely process connection credentials.",
            code="CONNECTION_ENCRYPTION_ERROR",
            status_code=500,
        )


class ConnectionCreationError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Unable to create the connection.",
            code="CONNECTION_CREATION_ERROR",
            status_code=500,
        )


class ConnectionUpdateError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Unable to update the connection.",
            code="CONNECTION_UPDATE_ERROR",
            status_code=500,
        )


class ConnectionDeletionError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Unable to delete the connection.",
            code="CONNECTION_DELETION_ERROR",
            status_code=500,
        )


class ConnectionTestError(AppException):
    def __init__(
        self,
        message: str = "Unable to test the database connection.",
    ) -> None:
        super().__init__(
            message,
            code="CONNECTION_TEST_FAILED",
            status_code=400,
        )


class ConnectionAuthenticationError(ConnectionTestError):
    def __init__(self) -> None:
        super().__init__(
            "Database authentication failed. Please verify the username and password."
        )


class ConnectionHostError(ConnectionTestError):
    def __init__(self) -> None:
        super().__init__(
            "Unable to connect to the database host. Please verify the host and port."
        )


class ConnectionDatabaseError(ConnectionTestError):
    def __init__(self) -> None:
        super().__init__(
            "The specified database could not be accessed."
        )


class ConnectionTimeoutError(ConnectionTestError):
    def __init__(self) -> None:
        super().__init__(
            "The database connection timed out."
        )


class ConnectionUnsupportedTypeError(AppException):
    def __init__(
        self,
        connection_type: str,
    ) -> None:
        super().__init__(
            f"Connection type '{connection_type}' is not supported.",
            code="UNSUPPORTED_CONNECTION_TYPE",
            status_code=400,
        )