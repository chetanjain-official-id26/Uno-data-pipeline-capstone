import logging

from fastapi import APIRouter, status

from src.artifact.artifact_service import ArtifactService
from src.artifact.s3_uploader import S3Uploader
from src.artifact.wheel_builder import WheelBuilder
from src.airflow.airflow_service import AirflowService
from src.exceptions.deployment import (
    DeploymentError,
)
from src.repositories.connection_repository import ConnectionRepository
from src.repositories.pipeline_deployment import DeploymentRepository
from src.repositories.pipeline_repository import PipelineRepository
from src.repositories.target_repository import TargetRepository
from src.repositories.transformation_repository import (
    TransformationRepository,
)
from src.schema.request_response_schema.deployment import (
    DeploymentResponse,
)
from src.services.deployment import DeploymentService

logger = logging.getLogger(__name__)


# ============================================================
# DEPENDENCIES
# ============================================================

pipeline_repository = PipelineRepository()
connection_repository = ConnectionRepository()
transformation_repository = TransformationRepository()
target_repository = TargetRepository()
deployment_repository = DeploymentRepository()

wheel_builder = WheelBuilder()

s3_uploader = S3Uploader(
    bucket="YOUR_BUCKET_NAME",
)

artifact_service = ArtifactService(
    wheel_builder=wheel_builder,
    s3_uploader=s3_uploader,
)

airflow_service = AirflowService()

deployment_service = DeploymentService(
    pipeline_repository=pipeline_repository,
    connection_repository=connection_repository,
    transformation_repository=transformation_repository,
    target_repository=target_repository,
    deployment_repository=deployment_repository,
    artifact_service=artifact_service,
    airflow_service=airflow_service,
)


router = APIRouter(
    prefix="/pipelines",
    tags=["Deployments"],
)


# ============================================================
# DEPLOY PIPELINE
# ============================================================

@router.post(
    "/{pipeline_id}/deploy",
    response_model=DeploymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def deploy_pipeline(
    pipeline_id: str,
):
    """Deploy a pipeline."""

    if not pipeline_id.strip():
        logger.warning(
            "deployment_invalid_pipeline_id"
        )

        raise DeploymentError(
            "Pipeline ID cannot be empty.",
            code="INVALID_PIPELINE_ID",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    pipeline_id = pipeline_id.strip()

    try:
        logger.info(
            "pipeline_deployment_started",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        result = await deployment_service.deploy(
            pipeline_id=pipeline_id,
        )

        logger.info(
            "pipeline_deployment_succeeded",
            extra={
                "pipeline_id": pipeline_id,
                "deployment_id": result.get(
                    "deployment_id"
                ),
                "version": result.get(
                    "version"
                ),
            },
        )

        return result

    except DeploymentError:
        logger.warning(
            "pipeline_deployment_error",
            extra={
                "pipeline_id": pipeline_id,
            },
        )
        raise

    except ValueError as exc:
        logger.warning(
            "pipeline_deployment_validation_error",
            extra={
                "pipeline_id": pipeline_id,
                "error": str(exc),
            },
        )

        raise DeploymentError(
            str(exc),
            code="DEPLOYMENT_VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from exc

    except Exception:
        logger.exception(
            "pipeline_deployment_unexpected_error",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        raise DeploymentError(
            "Pipeline deployment failed.",
            code="DEPLOYMENT_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )