from src.exceptions.base import AppException


class PipelineNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "The requested pipeline was not found.",
            code="PIPELINE_NOT_FOUND",
            status_code=404,
        )


class PipelineValidationError(AppException):
    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(
            message,
            code="PIPELINE_VALIDATION_ERROR",
            status_code=400,
        )


class PipelineNameRequiredError(PipelineValidationError):
    def __init__(self) -> None:
        super().__init__(
            "Pipeline name is required."
        )


class PipelineSourceRequiredError(PipelineValidationError):
    def __init__(self) -> None:
        super().__init__(
            "A source connection is required for the pipeline."
        )


class PipelineSourceTableRequiredError(PipelineValidationError):
    def __init__(self) -> None:
        super().__init__(
            "A source table is required for the pipeline."
        )


class PipelineAlreadyExistsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "A pipeline with this configuration already exists.",
            code="PIPELINE_ALREADY_EXISTS",
            status_code=409,
        )


class PipelineCreationError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Unable to create the pipeline.",
            code="PIPELINE_CREATION_ERROR",
            status_code=500,
        )


class PipelineUpdateError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Unable to update the pipeline.",
            code="PIPELINE_UPDATE_ERROR",
            status_code=500,
        )


class PipelineDeletionError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Unable to delete the pipeline.",
            code="PIPELINE_DELETION_ERROR",
            status_code=500,
        )


class PipelineSourceConnectionError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "The pipeline source connection could not be loaded.",
            code="PIPELINE_SOURCE_CONNECTION_ERROR",
            status_code=400,
        )


class PipelineTargetRequiredError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "A target configuration is required before deployment.",
            code="PIPELINE_TARGET_REQUIRED",
            status_code=400,
        )