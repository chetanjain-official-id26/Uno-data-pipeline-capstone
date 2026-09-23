import logging

from fastapi import APIRouter, HTTPException, status

from src.engine.target_writer import TargetWriter

from src.repositories.connection_repository import ConnectionRepository
from src.repositories.pipeline_repository import PipelineRepository
from src.repositories.target_repository import TargetRepository

from src.schema.request_response_schema.target import (
    TargetCreate,
    TargetResponse,
    TargetUpdate,
)

from src.services.target_service import TargetService


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/pipelines",
    tags=["Targets"],
)


target_repository = TargetRepository()
pipeline_repository = PipelineRepository()
connection_repository = ConnectionRepository()
target_writer = TargetWriter()


target_service = TargetService(
    target_repository=target_repository,
    pipeline_repository=pipeline_repository,
    connection_repository=connection_repository,
    target_writer=target_writer,
)


@router.post(
    "/{pipeline_id}/target",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def create_target(
    pipeline_id: str,
    data: TargetCreate,
):
    """
    Create a target configuration for a pipeline.

    Takes a pipeline ID and target configuration, validates the
    target details, persists the target configuration, and returns
    the generated target ID.

    Raises an HTTP 400 error when the pipeline ID or target
    configuration is invalid.
    """
    if not pipeline_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline ID cannot be empty",
        )

    try:
        target_id = await target_service.create_target(
            pipeline_id=pipeline_id,
            data=data.model_dump(),
        )

        return {
            "id": target_id,
            "message": "Target configuration created successfully",
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{pipeline_id}/target",
    response_model=TargetResponse,
    status_code=status.HTTP_200_OK,
)
async def get_target(
    pipeline_id: str,
):
    """
    Retrieve the target configuration for a pipeline.

    Takes a pipeline ID, retrieves the corresponding target
    configuration, and returns the destination details.

    Raises an HTTP 400 error when the pipeline ID is invalid
    and an HTTP 404 error when the target configuration does
    not exist.
    """
    if not pipeline_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline ID cannot be empty",
        )

    try:
        target = await target_service.get_target(
            pipeline_id=pipeline_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target configuration not found",
        )

    return target


@router.patch(
    "/{pipeline_id}/target",
    status_code=status.HTTP_200_OK,
)
async def update_target(
    pipeline_id: str,
    data: TargetUpdate,
):
    """
    Update a pipeline target configuration.

    Takes a pipeline ID and the target fields to update, modifies
    the existing target configuration, and returns a success message.

    Raises an HTTP 400 error when the pipeline ID or update data
    is invalid and an HTTP 404 error when the target configuration
    does not exist.
    """
    if not pipeline_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline ID cannot be empty",
        )

    update_data = data.model_dump(
        exclude_unset=True,
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field is required for update",
        )

    try:
        updated = await target_service.update_target(
            pipeline_id=pipeline_id,
            data=update_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target configuration not found",
        )

    return {
        "message": "Target configuration updated successfully",
    }


@router.delete(
    "/{pipeline_id}/target",
    status_code=status.HTTP_200_OK,
)
async def delete_target(
    pipeline_id: str,
):
    """
    Delete a pipeline target configuration.

    Takes a pipeline ID, removes the corresponding target
    configuration, and returns a success message.

    Raises an HTTP 400 error when the pipeline ID is invalid
    and an HTTP 404 error when the target configuration does
    not exist.
    """
    if not pipeline_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline ID cannot be empty",
        )

    try:
        deleted = await target_service.delete_target(
            pipeline_id=pipeline_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target configuration not found",
        )

    return {
        "message": "Target configuration deleted successfully",
    }