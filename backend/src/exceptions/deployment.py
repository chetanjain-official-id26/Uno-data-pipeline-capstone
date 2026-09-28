from src.exceptions.exceptions import AppException


class DeploymentError(AppException):
    """Base exception for pipeline deployment failures."""

    def __init__(
        self,
        message: str = "Pipeline deployment failed.",
        *,
        code: str = "DEPLOYMENT_ERROR",
        status_code: int = 500,
    ) -> None:
        super().__init__(
            message,
            code=code,
            status_code=status_code,
        )


class PipelineNotFoundError(DeploymentError):
    def __init__(self) -> None:
        super().__init__(
            "Pipeline was not found.",
            code="PIPELINE_NOT_FOUND",
            status_code=404,
        )


class SourceConnectionNotFoundError(DeploymentError):
    def __init__(self) -> None:
        super().__init__(
            "Source connection was not found.",
            code="SOURCE_CONNECTION_NOT_FOUND",
            status_code=404,
        )


class SourceConfigurationError(DeploymentError):
    def __init__(
        self,
        message: str = "Source configuration is invalid.",
    ) -> None:
        super().__init__(
            message,
            code="SOURCE_CONFIGURATION_ERROR",
            status_code=400,
        )


class TargetNotFoundError(DeploymentError):
    def __init__(self) -> None:
        super().__init__(
            "Target configuration was not found.",
            code="TARGET_NOT_FOUND",
            status_code=404,
        )


class TargetConnectionNotFoundError(DeploymentError):
    def __init__(self) -> None:
        super().__init__(
            "Target connection was not found.",
            code="TARGET_CONNECTION_NOT_FOUND",
            status_code=404,
        )


class TargetConfigurationError(DeploymentError):
    def __init__(
        self,
        message: str = "Target configuration is invalid.",
    ) -> None:
        super().__init__(
            message,
            code="TARGET_CONFIGURATION_ERROR",
            status_code=400,
        )


class TransformationConfigurationError(DeploymentError):
    def __init__(
        self,
        message: str = "Transformation configuration is invalid.",
    ) -> None:
        super().__init__(
            message,
            code="TRANSFORMATION_CONFIGURATION_ERROR",
            status_code=400,
        )


class ArtifactBuildError(DeploymentError):
    def __init__(
        self,
        message: str = "Failed to build deployment artifact.",
    ) -> None:
        super().__init__(
            message,
            code="ARTIFACT_BUILD_ERROR",
            status_code=500,
        )


class ArtifactUploadError(DeploymentError):
    def __init__(
        self,
        message: str = "Failed to upload deployment artifact.",
    ) -> None:
        super().__init__(
            message,
            code="ARTIFACT_UPLOAD_ERROR",
            status_code=500,
        )


class AirflowDeploymentError(DeploymentError):
    def __init__(
        self,
        message: str = "Failed to deploy pipeline to Airflow.",
    ) -> None:
        super().__init__(
            message,
            code="AIRFLOW_DEPLOYMENT_ERROR",
            status_code=500,
        )


class DeploymentRecordError(DeploymentError):
    def __init__(
        self,
        message: str = "Failed to persist deployment information.",
    ) -> None:
        super().__init__(
            message,
            code="DEPLOYMENT_RECORD_ERROR",
            status_code=500,
        )