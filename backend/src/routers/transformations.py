from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from src.repositories.connection_repository import ConnectionRepository
from src.repositories.transformation_repository import TransformationRepository
from src.schema.request_response_schema.transform import (
    TransformationCreate,
    TransformationUpdate,
)

router = APIRouter(
    prefix="/transformations",
    tags=["Transformations"],
)

transformation_repository = TransformationRepository()
connection_repository = ConnectionRepository()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_transformation(data: TransformationCreate):
    """Create a transformation step for a stored connection.

    The client provides connection_id.
    pipeline_id is obtained from the stored connection.
    """
    # ---------------------------------------------------------
    # 1. Validate connection_id
    # ---------------------------------------------------------
    connection_id = data.connection_id.strip()

    if not connection_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection ID cannot be empty",
        )

    # ---------------------------------------------------------
    # 2. Get connection
    # ---------------------------------------------------------
    connection = await connection_repository.get_by_id(connection_id)

    if connection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # ---------------------------------------------------------
    # 3. Get pipeline_id from connection
    # ---------------------------------------------------------
    pipeline_id = connection.get("pipeline_id")

    if not pipeline_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The connection does not have a pipeline_id",
        )

    # ---------------------------------------------------------
    # 4. Check whether this step already exists
    # ---------------------------------------------------------
    existing_step = await transformation_repository.get_step(
        connection_id=connection_id,
        step_order=data.step_order,
    )

    if existing_step is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Transformation step {data.step_order} "
                f"already exists for this connection"
            ),
        )

    # ---------------------------------------------------------
    # 5. Build transformation document
    # ---------------------------------------------------------
    now = datetime.now(timezone.utc)

    transformation = {
        "pipeline_id": pipeline_id,
        "connection_id": connection_id,
        "step_order": data.step_order,
        "sql_query": data.sql_query,
        "input_view": data.input_view,
        "output_view": f"step_{data.step_order}_out",
        "enabled": True,
        "created_at": now,
        "updated_at": now,
    }

    # ---------------------------------------------------------
    # 6. Save transformation
    # ---------------------------------------------------------
    transformation_id = await transformation_repository.create(transformation)

    # ---------------------------------------------------------
    # 7. Response
    # ---------------------------------------------------------
    return {
        "id": transformation_id,
        "pipeline_id": pipeline_id,
        "connection_id": connection_id,
        "step_order": data.step_order,
        "input_view": data.input_view,
        "output_view": f"step_{data.step_order}_out",
        "sql_query": data.sql_query,
        "enabled": True,
        "message": "Transformation created successfully",
    }


@router.get(
    "/{connection_id}",
    status_code=status.HTTP_200_OK,
)
async def get_transformations(connection_id: str):
    """Retrieve all enabled transformation steps for a connection."""
    connection_id = connection_id.strip()

    if not connection_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection ID cannot be empty",
        )

    transformations = await transformation_repository.get_by_connection(
        connection_id
    )

    result = []
    for transformation in transformations:
        transformation["id"] = str(transformation["_id"])
        del transformation["_id"]
        result.append(transformation)

    return result


@router.get(
    "/{connection_id}/step/{step_order}",
    status_code=status.HTTP_200_OK,
)
async def get_transformation_step(
    connection_id: str,
    step_order: int,
):
    """Retrieve a specific transformation step for a connection."""
    connection_id = connection_id.strip()

    if not connection_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection ID cannot be empty",
        )

    if step_order < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Step order must be greater than or equal to 1",
        )

    transformation = await transformation_repository.get_step(
        connection_id=connection_id,
        step_order=step_order,
    )

    if transformation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transformation not found",
        )

    transformation["id"] = str(transformation["_id"])
    del transformation["_id"]

    return transformation