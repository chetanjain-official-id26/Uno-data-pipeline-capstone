from typing import Any

from src.repositories.connection_repository import (
ConnectionRepository,
)
from src.repositories.pipeline_repository import (
PipelineRepository,
)

class PipelineService:
 """Business logic for pipeline management."""


def __init__(
    self,
    pipeline_repository: PipelineRepository,
    connection_repository: ConnectionRepository,
) -> None:
    self.pipeline_repository = pipeline_repository
    self.connection_repository = connection_repository

async def create_pipeline(
    self,
    name: str,
) -> str:

    name = name.strip()

    if not name:
        raise ValueError(
            "Pipeline name cannot be empty"
        )

    document = {
        "name": name,
        "source_id": None,
        "source_table": None,
    }

    return await self.pipeline_repository.create(
        document
    )

async def get_pipeline(
    self,
    pipeline_id: str,
) -> dict[str, Any] | None:

    pipeline = (
        await self.pipeline_repository.get_by_id(
            pipeline_id
        )
    )

    if not pipeline:
        return None

    return self._serialize_pipeline(
        pipeline
    )

async def get_all_pipelines(
    self,
) -> list[dict[str, Any]]:

    pipelines = (
        await self.pipeline_repository.get_all()
    )

    return [
        self._serialize_pipeline(
            pipeline
        )
        for pipeline in pipelines
    ]

async def update_pipeline(
    self,
    pipeline_id: str,
    data: dict[str, Any],
) -> bool:

    update_data: dict[str, Any] = {}

    if "name" in data and data["name"] is not None:
        name = data["name"].strip()

        if not name:
            raise ValueError(
                "Pipeline name cannot be empty"
            )

        update_data["name"] = name

    if (
        "source_connection_id" in data
        and data["source_connection_id"] is not None
    ):
        connection_id = (
            data["source_connection_id"].strip()
        )

        if not connection_id:
            raise ValueError(
                "Source connection ID cannot be empty"
            )

        connection = (
            await self.connection_repository.get_by_id(
                connection_id
            )
        )

        if not connection:
            raise ValueError(
                "Source connection not found"
            )

        update_data["source_id"] = connection_id

        # If no source table was explicitly supplied,
        # preserve the table saved on the connection.
        if (
            "source_table" not in data
            or data["source_table"] is None
        ):
            connection_table = connection.get(
                "table_name"
            )

            if connection_table:
                update_data["source_table"] = (
                    connection_table
                )

    if (
        "source_table" in data
        and data["source_table"] is not None
    ):
        source_table = data["source_table"].strip()

        if not source_table:
            raise ValueError(
                "Source table cannot be empty"
            )

        update_data["source_table"] = source_table

    if not update_data:
        raise ValueError(
            "No pipeline fields to update"
        )

    return await self.pipeline_repository.update(
        pipeline_id,
        update_data,
    )

async def delete_pipeline(
    self,
    pipeline_id: str,
) -> bool:

    return await self.pipeline_repository.delete(
        pipeline_id
    )

@staticmethod
def _serialize_pipeline(
    pipeline: dict[str, Any],
) -> dict[str, Any]:

    pipeline_id = pipeline.get("_id")

    return {
        "id": str(pipeline_id),
        "name": pipeline.get("name"),
        "source_connection_id": (
            str(pipeline["source_id"])
            if pipeline.get("source_id") is not None
            else None
        ),
        "source_table": pipeline.get(
            "source_table"
        ),
        "status": pipeline.get(
            "status",
            "draft",
        ),
        "created_at": pipeline.get(
            "created_at"
        ),
        "updated_at": pipeline.get(
            "updated_at"
        ),
    }

