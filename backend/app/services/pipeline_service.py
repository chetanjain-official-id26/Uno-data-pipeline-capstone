from app.repositories.pipeline_repository import (
    PipelineRepository,
)


class PipelineService:

    def __init__(
        self,
        repository: PipelineRepository,
    ):
        self.repository = repository

    async def create_pipeline(
        self,
        data: dict,
    ):

        return await self.repository.create(
            data
        )

    async def get_pipeline(
        self,
        pipeline_id: str,
    ):

        return await self.repository.get_by_id(
            pipeline_id
        )

    async def list_pipelines(self):

        return await self.repository.get_all()