
import logging

from fastapi import APIRouter, HTTPException, status

from src.airflow.airflow_service import AirflowService
from src.repositories.pipeline_deployment import DeploymentRepository
from src.services.run_service import RunService


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/pipelines",
    tags=["Runs"],
)


deployment_repository = DeploymentRepository()
airflow_service = AirflowService()

run_service = RunService(
    deployment_repository=deployment_repository,
    airflow_service=airflow_service,
)


@router.post(
    "/{pipeline_id}/run",
    response_model=dict,
    status_code=status.HTTP_202_ACCEPTED,
)
async def run_pipeline(
    pipeline_id: str,
):
    """
    Trigger the currently deployed version of a pipeline.
    """

    if not pipeline_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline ID cannot be empty",
        )

    try:
        result = await run_service.run(
            pipeline_id=pipeline_id,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Failed to run pipeline: %s",
            pipeline_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start pipeline run",
        ) from exc

