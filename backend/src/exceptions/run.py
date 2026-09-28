from src.exceptions.base import AppException


class RunValidationError(AppException):
    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(
            message,
            code="RUN_VALIDATION_ERROR",
            status_code=400,
        )


class DeploymentRequiredForRunError(RunValidationError):
    def __init__(self) -> None:
        super().__init__(
            "The pipeline must be successfully deployed before it can be run."
        )


class DeploymentNotFoundForRunError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "No deployed version was found for this pipeline.",
            code="DEPLOYMENT_NOT_FOUND_FOR_RUN",
            status_code=404,
        )


class RunAlreadyInProgressError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "A run is already in progress for this pipeline.",
            code="RUN_ALREADY_IN_PROGRESS",
            status_code=409,
        )


class RunAirflowError(AppException):
    def __init__(
        self,
        message: str = "Unable to start the pipeline in Airflow.",
    ) -> None:
        super().__init__(
            message,
            code="RUN_AIRFLOW_ERROR",
            status_code=500,
        )


class RunTriggerError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "Unable to trigger the pipeline run.",
            code="RUN_TRIGGER_ERROR",
            status_code=500,
        )


class RunNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            "The requested pipeline run was not found.",
            code="RUN_NOT_FOUND",
            status_code=404,
        )