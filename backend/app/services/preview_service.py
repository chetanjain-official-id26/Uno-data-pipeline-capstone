from app.execution.preview_executor import (
    PreviewExecutor
)

from app.repositories.transformation_repository import (
    TransformationRepository
)


class PreviewService:

    def __init__(self):

        self.repository = (
            TransformationRepository()
        )

        self.executor = (
            PreviewExecutor()
        )

    def preview(
        self,
        pipeline_id: str,
        step_order: int,
        source_documents: list[dict],
        preview_limit: int = 100
    ):

        transformations = (
            self.repository
            .get_by_pipeline(
                pipeline_id
            )
        )

        if not transformations:

            raise ValueError(
                "No transformations found"
            )

        target_step = (
            self.repository
            .get_step(
                pipeline_id,
                step_order
            )
        )

        if not target_step:

            raise ValueError(
                "Transformation step not found"
            )

        return self.executor.execute(
            transformations=transformations,
            source_documents=source_documents,
            target_step=step_order,
            preview_limit=preview_limit
        )