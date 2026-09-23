from fastapi import APIRouter, HTTPException, status

from src.repositories.transformation_repository import (
    TransformationRepository,
)
from src.schema.request_response_schema.transform import (
    TransformationCreate,
    TransformationUpdate,
)

router = APIRouter(
    prefix="/transformations",
    tags=["Transformations"],
)

repository = TransformationRepository()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_transformation(
    data: TransformationCreate,
):
    """Create a new transformation step for a connection.

    The connection_id is taken from the request body and used to
    associate the transformation with the stored database connection.
    """
    transformation = data.model_dump()

    connection_id = transformation.get("connection_id")

    if not connection_id or not connection_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection ID cannot be empty",
        )

    transformation["output_view"] = f"step_{data.step_order}_out"
    transformation["enabled"] = True

    transformation_id = await repository.create(transformation)

    return {
        "id": transformation_id,
        "message": "Transformation created successfully",
    }


@router.get(
    "/{connection_id}",
    status_code=status.HTTP_200_OK,
)
async def get_transformations(
    connection_id: str,
):
    """Retrieve all transformation steps for a connection.

    Takes a connection ID, retrieves all enabled transformation
    steps from the database, orders them by step order, and
    returns the transformation configurations.
    """
    if not connection_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection ID cannot be empty",
        )

    transformations = await repository.get_by_connection(connection_id)

    for transformation in transformations:
        transformation["id"] = str(transformation["_id"])
        del transformation["_id"]

    return transformations


@router.get(
    "/{connection_id}/step/{step_order}",
    status_code=status.HTTP_200_OK,
)
async def get_transformation_step(
    connection_id: str,
    step_order: int,
):
    """Retrieve a specific transformation step for a connection.

    Takes a connection ID and step order, retrieves the corresponding
    transformation configuration, and returns its details.
    """
    if not connection_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection ID cannot be empty",
        )

    if step_order < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Step order must be greater than or equal to 1",
        )

    transformation = await repository.get_step(
        connection_id,
        step_order,
    )

    if not transformation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transformation not found",
        )

    transformation["id"] = str(transformation["_id"])
    del transformation["_id"]

    return transformation