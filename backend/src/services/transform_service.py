from src.execution.preview_executor import (
    PreviewExecutor,
)
from src.repositories.connection_repository import (
    ConnectionRepository,
)
from src.repositories.transformation_repository import (
    TransformationRepository,
)


class TransformationService:
    """Business logic for transformation preview."""

    def __init__(
        self,
        connection_repository: ConnectionRepository,
        transformation_repository: TransformationRepository,
        preview_executor: PreviewExecutor | None = None,
    ) -> None:
        self.connection_repository = (
            connection_repository
        )
        self.transformation_repository = (
            transformation_repository
        )
        self.preview_executor = (
            preview_executor
            or PreviewExecutor()
        )

    async def preview(
        self,
        connection_id: str,
        target_step_order: int,
    ) -> dict:
        if not connection_id or not connection_id.strip():
            raise ValueError(
                "Connection ID cannot be empty"
            )

        if target_step_order < 0:
            raise ValueError(
                "Target step order cannot be negative"
            )

        connection_id = connection_id.strip()

        connection = (
            await self.connection_repository
            .get_by_id(connection_id)
        )

        if connection is None:
            raise ValueError(
                "Connection not found"
            )

        steps = (
            await self.transformation_repository
            .get_enabled_up_to_step(
                connection_id=connection_id,
                target_step_order=target_step_order,
            )
        )

        if not steps:
            raise ValueError(
                "No transformation steps found for this connection"
            )

        config = connection.get("config")

        if not config:
            raise ValueError(
                "Connection configuration is missing"
            )

        source_table = (
            connection.get("table_name")
            or config.get("table_name")
            or config.get("source_table")
        )

        if not source_table:
            raise ValueError(
                "Source table is missing from connection configuration"
            )

        return self.preview_executor.preview(
            connection=connection,
            source_table=source_table,
            steps=steps,
            target_step_order=target_step_order,
        )