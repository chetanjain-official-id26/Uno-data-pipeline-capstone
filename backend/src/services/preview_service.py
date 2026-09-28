from typing import Any

from src.execution.preview_executor import PreviewExecutor
from src.repositories.connection_repository import ConnectionRepository
from src.repositories.transformation_repository import TransformationRepository


class PreviewService:
    """Generate a preview using a stored database connection."""

    def __init__(self) -> None:
        self.connection_repository = ConnectionRepository()
        self.transformation_repository = TransformationRepository()
        self.executor = PreviewExecutor()

    async def preview(self, connection_id: str) -> dict[str, Any]:
        # --------------------------------------------------
        # 1. Validate connection ID
        # --------------------------------------------------
        if not connection_id or not connection_id.strip():
            raise ValueError("Connection ID cannot be empty")

        connection_id = connection_id.strip()

        # --------------------------------------------------
        # 2. Get stored connection
        # --------------------------------------------------
        connection = await self.connection_repository.get_by_id(connection_id)

        if connection is None:
            raise ValueError("Connection not found")

        # --------------------------------------------------
        # 3. Get stored source table
        # --------------------------------------------------
        source_table = connection.get("table_name")

        if not source_table:
            raise ValueError(
                "No source table has been stored for this connection. "
                "Test the connection and select a table first."
            )

        # --------------------------------------------------
        # 4. Get transformations
        # --------------------------------------------------
        transformations = (
            await self.transformation_repository.get_by_connection(
                connection_id
            )
        )

        # --------------------------------------------------
        # 5. Execute preview
        # --------------------------------------------------
        result = self.executor.preview(
            connection=connection,
            source_table=source_table,
            steps=transformations,
        )

        # --------------------------------------------------
        # 6. Add connection ID
        # --------------------------------------------------
        result["connection_id"] = connection_id

        return result