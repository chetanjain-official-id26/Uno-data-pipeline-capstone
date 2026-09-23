from src.engine.target_writer import TargetWriter
from src.engine.table_validator import validate_table_name
from src.repositories.pipeline_repository import PipelineRepository
from src.repositories.target_repository import TargetRepository


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
        # 1. Verify pipeline exists
        pipeline = await self.pipeline_repository.get_by_id(
            pipeline_id
        )

        if not pipeline:
            raise ValueError(
                "Pipeline not found"
            )

        # 2. Validate target table name
        validate_table_name(
            data["target_table"]
        )

        # 3. connection_id is required
        connection_id = data.get("connection_id")

        if not connection_id:
            raise ValueError(
                "Target connection ID is required"
            )

        # 4. Verify connection exists
        connection = await self.connection_repository.get_by_id(
            connection_id
        )

        if not connection:
            raise ValueError(
                "Target connection not found"
            )

        # 5. One connection can have only ONE target
        existing_target = (
            await self.target_repository.get_by_connection_id(
                connection_id
            )
        )

        if existing_target:
            raise ValueError(
                "A target already exists for this connection"
            )

        # 6. Create target
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

            # Find the existing target for this pipeline
            existing_target = (
                await self.target_repository.get_by_pipeline(
                    pipeline_id
                )
            )

            # If changing connection_id, make sure that connection
            # isn't already assigned to another target.
            if existing_target:
                existing_target_id = str(
                    existing_target["_id"]
                )

                connection_target = (
                    await self.target_repository
                    .get_by_connection_id(
                        data["connection_id"]
                    )
                )

                if (
                    connection_target
                    and str(connection_target["_id"])
                    != existing_target_id
                ):
                    raise ValueError(
                        "A target already exists for this connection"
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