from src.exceptions.base import AppException


class PreviewValidationError(AppException):
    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(
            message,
            code="PREVIEW_VALIDATION_ERROR",
            status_code=400,
        )


class PreviewConnectionRequiredError(
    PreviewValidationError
):
    def __init__(self) -> None:
        super().__init__(
            "A connection ID is required to generate a preview."
        )


class PreviewConnectionNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "The connection required for preview was not found.",
            code="PREVIEW_CONNECTION_NOT_FOUND",
            status_code=404,
        )


class PreviewExecutionError(AppException):
    def __init__(
        self,
        message: str = "Unable to generate the data preview.",
    ) -> None:
        super().__init__(
            message,
            code="PREVIEW_EXECUTION_ERROR",
            status_code=400,
        )


class PreviewQueryError(PreviewExecutionError):
    def __init__(self) -> None:
        super().__init__(
            "The preview query could not be executed."
        )


class PreviewTimeoutError(PreviewExecutionError):
    def __init__(self) -> None:
        super().__init__(
            "The preview operation timed out."
        )