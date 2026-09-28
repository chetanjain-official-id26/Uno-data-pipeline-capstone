from src.exceptions.base import AppException


class TransformationNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "The requested transformation was not found.",
            code="TRANSFORMATION_NOT_FOUND",
            status_code=404,
        )


class TransformationValidationError(AppException):
    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(
            message,
            code="TRANSFORMATION_VALIDATION_ERROR",
            status_code=400,
        )


class TransformationConnectionRequiredError(
    TransformationValidationError
):
    def __init__(self) -> None:
        super().__init__(
            "A connection ID is required for the transformation."
        )


class TransformationStepOrderError(
    TransformationValidationError
):
    def __init__(self) -> None:
        super().__init__(
            "Transformation step order must be greater than or equal to 1."
        )


class TransformationSqlRequiredError(
    TransformationValidationError
):
    def __init__(self) -> None:
        super().__init__(
            "SQL query is required for the transformation."
        )


class TransformationInputViewError(
    TransformationValidationError
):
    def __init__(self) -> None:
        super().__init__(
            "Input view is required for the transformation."
        )


class TransformationAlreadyExistsError(AppException):
    def __init__(
        self,
        step_order: int,
    ) -> None:
        super().__init__(
            f"Transformation step {step_order} already exists.",
            code="TRANSFORMATION_ALREADY_EXISTS",
            status_code=409,
        )


class TransformationCreationError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Unable to create the transformation.",
            code="TRANSFORMATION_CREATION_ERROR",
            status_code=500,
        )


class TransformationUpdateError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Unable to update the transformation.",
            code="TRANSFORMATION_UPDATE_ERROR",
            status_code=500,
        )


class TransformationExecutionError(AppException):
    def __init__(
        self,
        message: str = "Unable to execute the transformation.",
    ) -> None:
        super().__init__(
            message,
            code="TRANSFORMATION_EXECUTION_ERROR",
            status_code=400,
        )