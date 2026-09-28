import logging

from fastapi import APIRouter, HTTPException, status

from src.exceptions.exceptions import DatabaseError
from src.repositories.pipeline_repository import (
    PipelineRepository,
)
from src.schema.request_response_schema.pipeline import (
    PipelineCreate,
    PipelineUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/pipelines",
    tags=["Pipelines"],
)

repository = PipelineRepository()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_pipeline(
    data: PipelineCreate,
):
    """Create a new data pipeline.

    Takes a pipeline name, source connection ID, and source table, persists the
    pipeline with draft status, and returns the generated pipeline ID.
    """
    try:
        pipeline_id = await repository.create(data.model_dump())

        logger.info(
            "Pipeline created successfully",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        return {
            "id": pipeline_id,
            "message": "Pipeline created successfully",
        }

    except DatabaseError:
        logger.exception("Database error while creating pipeline")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create pipeline",
        ) from None

    except Exception:
        logger.exception("Unexpected error while creating pipeline")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create pipeline",
        ) from None


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def get_pipelines():
    """Retrieve all data pipelines.

    Retrieves all pipeline configurations from the database, converts MongoDB
    IDs into string IDs, and returns the complete list of pipelines.
    """
    try:
        pipelines = await repository.get_all()

        for pipeline in pipelines:
            pipeline["id"] = str(pipeline["_id"])

            del pipeline["_id"]

        logger.info(
            "Pipelines retrieved successfully",
            extra={
                "pipeline_count": len(pipelines),
            },
        )

        return pipelines

    except DatabaseError:
        logger.exception("Database error while retrieving pipelines")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pipelines",
        ) from None

    except Exception:
        logger.exception("Unexpected error while retrieving pipelines")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pipelines",
        ) from None


@router.get(
    "/{pipeline_id}",
    status_code=status.HTTP_200_OK,
)
async def get_pipeline(
    pipeline_id: str,
):
    """Retrieve a data pipeline by ID.

    Takes a pipeline ID, retrieves the corresponding pipeline configuration
    from the database, and returns its details.

    Raises HTTP 400 when the pipeline ID is empty or invalid. Raises HTTP 404
    when the pipeline does not exist.
    """
    if not pipeline_id.strip():
        logger.warning("Empty pipeline ID received")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline ID cannot be empty",
        )

    pipeline_id = pipeline_id.strip()

    try:
        pipeline = await repository.get_by_id(pipeline_id)

        if not pipeline:
            logger.warning(
                "Pipeline not found",
                extra={
                    "pipeline_id": pipeline_id,
                },
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pipeline not found",
            )

        pipeline["id"] = str(pipeline["_id"])

        del pipeline["_id"]

        logger.info(
            "Pipeline retrieved successfully",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        return pipeline

    except HTTPException:
        raise

    except DatabaseError:
        logger.exception(
            "Database error while retrieving pipeline",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pipeline",
        ) from None

    except Exception:
        logger.exception(
            "Unexpected error while retrieving pipeline",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pipeline",
        ) from None


@router.patch(
    "/{pipeline_id}",
    status_code=status.HTTP_200_OK,
)
async def update_pipeline(
    pipeline_id: str,
    data: PipelineUpdate,
):
    """Update an existing data pipeline.

    Raises HTTP 400 when the pipeline ID is empty or no fields are provided for
    update.

    Raises HTTP 404 when the pipeline does not exist.
    """
    if not pipeline_id.strip():
        logger.warning("Empty pipeline ID received for update")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline ID cannot be empty",
        )

    pipeline_id = pipeline_id.strip()

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        logger.warning(
            "Pipeline update requested without fields",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    try:
        updated = await repository.update(
            pipeline_id,
            update_data,
        )

        if not updated:
            logger.warning(
                "Pipeline not found during update",
                extra={
                    "pipeline_id": pipeline_id,
                },
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pipeline not found",
            )

        logger.info(
            "Pipeline updated successfully",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        return {
            "id": pipeline_id,
            "message": "Pipeline updated successfully",
        }

    except HTTPException:
        raise

    except DatabaseError:
        logger.exception(
            "Database error while updating pipeline",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update pipeline",
        ) from None

    except Exception:
        logger.exception(
            "Unexpected error while updating pipeline",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update pipeline",
        ) from None


@router.delete(
    "/{pipeline_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_pipeline(
    pipeline_id: str,
):
    """Delete a data pipeline by ID.

    Raises HTTP 400 when the pipeline ID is empty. Raises HTTP 404 when the
    pipeline does not exist.
    """
    if not pipeline_id.strip():
        logger.warning("Empty pipeline ID received for deletion")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline ID cannot be empty",
        )

    pipeline_id = pipeline_id.strip()

    try:
        deleted = await repository.delete(pipeline_id)

        if not deleted:
            logger.warning(
                "Pipeline not found during deletion",
                extra={
                    "pipeline_id": pipeline_id,
                },
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pipeline not found",
            )

        logger.info(
            "Pipeline deleted successfully",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        return {
            "id": pipeline_id,
            "message": "Pipeline deleted successfully",
        }

    except HTTPException:
        raise

    except DatabaseError:
        logger.exception(
            "Database error while deleting pipeline",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete pipeline",
        ) from None

    except Exception:
        logger.exception(
            "Unexpected error while deleting pipeline",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete pipeline",
        ) from None