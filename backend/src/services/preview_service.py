from src.execution.preview_executor import PreviewExecutor
from src.repositories.transformation_repository import (
    TransformationRepository,
)


class PreviewService:

    def __init__(self) -> None:
        self.repository = TransformationRepository()
        self.executor = PreviewExecutor()

    async def preview(
        self,
        connection_id: str,
        step_order: int,
        
        preview_limit: int = 100,
    ) -> dict:
        """Preview a transformation step using connection ID.

        Transformations are associated with a stored database connection,
        not a pipeline.
        """
        if not connection_id or not connection_id.strip():
            raise ValueError("Connection ID cannot be empty")

        if step_order < 1:
            raise ValueError("Step order must be greater than or equal to 1")

        if preview_limit < 1:
            raise ValueError("Preview limit must be greater than 0")

        transformations = await self.repository.get_by_connection(
            connection_id
        )

        if not transformations:
            raise ValueError("No transformations found for this connection")

        target_step = await self.repository.get_step(
            connection_id,
            step_order,
        )

        if not target_step:
            raise ValueError("Transformation step not found")

        return self.executor.execute(
            transformations=transformations,
            source_documents=source_documents,
            target_step=step_order,
            preview_limit=preview_limit,
        )