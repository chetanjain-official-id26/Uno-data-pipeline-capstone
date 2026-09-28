
import logging

from fastapi import APIRouter, HTTPException, status

from src.engine.target_writer import TargetWriter
from src.repositories.connection_repository import ConnectionRepository
from src.repositories.pipeline_repository import PipelineRepository
from src.repositories.target_repository import TargetRepository
from src.schema.request_response_schema.target import (
    TargetCreate,
    TargetResponse,
    TargetTestRequest,
    TargetTestResponse,
    TargetUpdate,
)
from src.services.target_service import TargetService


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/pipelines",
    tags=["Targets"],
)


# ============================================================
# DEPENDENCIES
# ============================================================

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


# ============================================================
# TEST TARGET
# ============================================================


@router.post(
    "/{pipeline_id}/target/test",
    response_model=TargetTestResponse,
    status_code=status.HTTP_200_OK,
)
async def test_target(
    pipeline_id: str,
    data: TargetTestRequest,
):
    """Test a stored connection as a target."""

    if not pipeline_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline ID cannot be empty",
        )

    try:
        result = await target_service.test_target(
            connection_id=data.connection_id,
            target_table=data.target_table,
            write_mode=data.write_mode.value,
        )

        return TargetTestResponse(**result)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "target_test_failed",
            extra={
                "pipeline_id": pipeline_id,
                "connection_id": data.connection_id,
                "target_table": data.target_table,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Target connection test failed",
        ) from exc


# ============================================================
# CREATE TARGET
# ============================================================


@router.post(
    "/{pipeline_id}/target",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def create_target(
    pipeline_id: str,
    data: TargetCreate,
):
    """Create a target configuration for a pipeline."""

    if not pipeline_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline ID cannot be empty",
        )

    try:
        target_data = data.model_dump()

        # Store enum value as a string in MongoDB.
        target_data["write_mode"] = data.write_mode.value

        target_id = await target_service.create_target(
            pipeline_id=pipeline_id,
            data=target_data,
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

    except Exception as exc:
        logger.exception(
            "target_creation_failed",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create target configuration",
        ) from exc


# ============================================================
# GET TARGET
# ============================================================


@router.get(
    "/{pipeline_id}/target",
    response_model=TargetResponse,
    status_code=status.HTTP_200_OK,
)
async def get_target(
    pipeline_id: str,
):
    """Retrieve the target configuration for a pipeline."""

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

    except Exception as exc:
        logger.exception(
            "target_fetch_failed",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch target configuration",
        ) from exc

    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target configuration not found",
        )

    return target


# ============================================================
# UPDATE TARGET
# ============================================================


@router.patch(
    "/{pipeline_id}/target",
    status_code=status.HTTP_200_OK,
)
async def update_target(
    pipeline_id: str,
    data: TargetUpdate,
):
    """Update a pipeline target configuration."""

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

    # Normalize enum to string before storing in MongoDB.
    if "write_mode" in update_data:
        update_data["write_mode"] = data.write_mode.value

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

    except Exception as exc:
        logger.exception(
            "target_update_failed",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update target configuration",
        ) from exc

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target configuration not found",
        )

    return {
        "message": "Target configuration updated successfully",
    }


# ============================================================
# DELETE TARGET
# ============================================================


@router.delete(
    "/{pipeline_id}/target",
    status_code=status.HTTP_200_OK,
)
async def delete_target(
    pipeline_id: str,
):
    """Delete a pipeline target configuration."""

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

    except Exception as exc:
        logger.exception(
            "target_deletion_failed",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete target configuration",
        ) from exc

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target configuration not found",
        )

    return {
        "message": "Target configuration deleted successfully",
    }

