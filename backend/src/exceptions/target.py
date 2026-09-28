from src.exceptions.base import AppException


class TargetNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "The target configuration was not found.",
            code="TARGET_NOT_FOUND",
            status_code=404,
        )


class TargetValidationError(AppException):
    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(
            message,
            code="TARGET_VALIDATION_ERROR",
            status_code=400,
        )


class TargetConnectionRequiredError(
    TargetValidationError
):
    def __init__(self) -> None:
        super().__init__(
            "A target connection is required."
        )


class TargetTableRequiredError(
    TargetValidationError
):
    def __init__(self) -> None:
        super().__init__(
            "A target table is required."
        )


class TargetWriteModeError(
    TargetValidationError
):
    def __init__(
        self,
        write_mode: str,
    ) -> None:
        super().__init__(
            f"Unsupported target write mode '{write_mode}'. "
            "Supported modes are APPEND and OVERWRITE."
        )


class TargetAlreadyExistsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "A target configuration already exists for this pipeline.",
            code="TARGET_ALREADY_EXISTS",
            status_code=409,
        )


class TargetCreationError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Unable to create the target configuration.",
            code="TARGET_CREATION_ERROR",
            status_code=500,
        )


class TargetUpdateError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Unable to update the target configuration.",
            code="TARGET_UPDATE_ERROR",
            status_code=500,
        )


class TargetDeletionError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Unable to delete the target configuration.",
            code="TARGET_DELETION_ERROR",
            status_code=500,
        )


class TargetTestError(AppException):
    def __init__(
        self,
        message: str = "Unable to test the target configuration.",
    ) -> None:
        super().__init__(
            message,
            code="TARGET_TEST_FAILED",
            status_code=400,
        )


class TargetConnectionNotFoundError(TargetTestError):
    def __init__(self) -> None:
        super().__init__(
            "The target connection was not found."
        )


class TargetTableAccessError(TargetTestError):
    def __init__(self) -> None:
        super().__init__(
            "The target table could not be accessed."
        )


class TargetWriteError(AppException):
    def __init__(
        self,
        message: str = "Unable to write data to the target.",
    ) -> None:
        super().__init__(
            message,
            code="TARGET_WRITE_ERROR",
            status_code=400,
        )