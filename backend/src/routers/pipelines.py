from fastapi import APIRouter, HTTPException, status

from src.repositories.pipeline_repository import (
    PipelineRepository,
)

from src.schema.request_response_schema.pipeline import (
    PipelineCreate,
    PipelineUpdate,
)

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
    """
    Create a new data pipeline.

    Takes a pipeline name, source connection ID, and source table,
    persists the pipeline with draft status, and returns the
    generated pipeline ID.
    """
    pipeline_id = await repository.create(
        data.model_dump()
    )

    return {
        "id": pipeline_id,
        "message": "Pipeline created successfully",
    }


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def get_pipelines():
    """
    Retrieve all data pipelines.

    Retrieves all pipeline configurations from the database,
    converts MongoDB IDs into string IDs, and returns the
    complete list of pipelines.
    """
    pipelines = await repository.get_all()

    for pipeline in pipelines:
        pipeline["id"] = str(
            pipeline["_id"]
        )

        del pipeline["_id"]

    return pipelines


@router.get(
    "/{pipeline_id}",
    status_code=status.HTTP_200_OK,
)
async def get_pipeline(
    pipeline_id: str,
):
    """
    Retrieve a data pipeline by ID.

    Takes a pipeline ID, retrieves the corresponding pipeline
    configuration from the database, and returns its details.

    Raises an HTTP 404 error when the pipeline does not exist.
    """
    pipeline = await repository.get_by_id(
        pipeline_id
    )

    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found",
        )

    pipeline["id"] = str(
        pipeline["_id"]
    )

    del pipeline["_id"]

    return pipeline


@router.patch(
    "/{pipeline_id}",
    status_code=status.HTTP_200_OK,
)
async def update_pipeline(
    pipeline_id: str,
    data: PipelineUpdate,
):
    """
    Update an existing data pipeline.

    Takes a pipeline ID and the fields to update, modifies the
    pipeline configuration, and returns a success message.

    Raises an HTTP 400 error when no fields are provided and
    an HTTP 404 error when the pipeline does not exist.
    """
    update_data = data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    updated = await repository.update(
        pipeline_id,
        update_data,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found",
        )

    return {
        "message": "Pipeline updated successfully",
    }


@router.delete(
    "/{pipeline_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_pipeline(
    pipeline_id: str,
):
    """
    Delete a data pipeline.

    Takes a pipeline ID, removes the corresponding pipeline
    configuration from the database, and returns a success message.

    Raises an HTTP 404 error when the pipeline does not exist.
    """
    deleted = await repository.delete(
        pipeline_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found",
        )

    return {
        "message": "Pipeline deleted successfully",
    }