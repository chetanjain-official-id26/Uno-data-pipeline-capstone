from app.core.encryption import credential_encryptor
from app.models.connection import (
    build_connection_document,
)
from app.repositories.connection_repository import (
    ConnectionRepository,
)
from app.repositories.pipeline_repository import (
    PipelineRepository,
)
from app.schemas.connection import (
    CreateConnectionRequest,
)


class ConnectionService:

    def __init__(
        self,
        repository: ConnectionRepository,
        pipeline_repository: PipelineRepository,
    ) -> None:

        self.repository = repository
        self.pipeline_repository = (
            pipeline_repository
        )

    async def create_connection(
        self,
        pipeline_id: str,
        request: CreateConnectionRequest,
        created_by: str,
    ) -> str:

        pipeline = (
            await self.pipeline_repository.get_by_id(
                pipeline_id
            )
        )

        if pipeline is None:
            raise ValueError(
                "Pipeline not found"
            )

        existing = (
            await self.repository.get_by_pipeline(
                pipeline_id
            )
        )

        if existing is not None:
            raise ValueError(
                "Connection already exists for this pipeline"
            )

        encrypted_password = (
            credential_encryptor.encrypt(
                request.password
            )
        )

        document = build_connection_document(
            pipeline_id=pipeline_id,
            name=request.name,
            connection_type=request.type,
            host=request.host,
            port=request.port,
            database=request.database,
            username=request.username,
            encrypted_password=encrypted_password,
            created_by=created_by,
        )

        return await self.repository.create(
            document
        )