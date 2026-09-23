from bson import ObjectId

from app.engine.target_writer import TargetWriter
from app.engine.table_validator import validate_table_name
from app.repositories.pipeline_repository import PipelineRepository
from app.repositories.target_repository import TargetRepository


class TargetService:

    def __init__(
        self,
        target_repository: TargetRepository,
        pipeline_repository: PipelineRepository,
        connection_repository,
        target_writer: TargetWriter,
    ):
        self.target_repository = target_repository
        self.pipeline_repository = pipeline_repository
        self.connection_repository = connection_repository
        self.target_writer = target_writer

    async def create_target(
        self,
        pipeline_id: str,
        data: dict,
    ):

        pipeline = await self.pipeline_repository.get_by_id(
            pipeline_id
        )

        if not pipeline:
            raise ValueError(
                "Pipeline not found"
            )

        validate_table_name(
            data["target_table"]
        )

        connection = await self.connection_repository.get_by_id(
            data["connection_id"]
        )

        if not connection:
            raise ValueError(
                "Target connection not found"
            )

        target_id = await self.target_repository.create(
            pipeline_id,
            data,
        )

        return target_id

    async def get_target(
        self,
        pipeline_id: str,
    ):

        target = await self.target_repository.get_by_pipeline(
            pipeline_id
        )

        if not target:
            return None

        target["id"] = str(target["_id"])
        del target["_id"]

        return target

    async def update_target(
        self,
        pipeline_id: str,
        data: dict,
    ):

        if "target_table" in data:
            validate_table_name(
                data["target_table"]
            )

        if "connection_id" in data:

            connection = (
                await self.connection_repository.get_by_id(
                    data["connection_id"]
                )
            )

            if not connection:
                raise ValueError(
                    "Target connection not found"
                )

        return await self.target_repository.update(
            pipeline_id,
            data,
        )

    async def delete_target(
        self,
        pipeline_id: str,
    ):

        return await self.target_repository.delete(
            pipeline_id
        )