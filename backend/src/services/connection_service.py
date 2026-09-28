from src.schema.models.connection import (
build_connection_document,
)
from src.repositories.connection_repository import (
ConnectionRepository,
)
from src.repositories.pipeline_repository import (
PipelineRepository,
)
from src.schema.request_response_schema.connection import (
CreateConnectionRequest,
)
from src.utils.encryption import credential_encryptor

class ConnectionService:
 """Application service for external database connections."""


def __init__(
    self,
    repository: ConnectionRepository,
    pipeline_repository: PipelineRepository,
) -> None:
    self.repository = repository
    self.pipeline_repository = pipeline_repository

async def create_connection(
    self,
    pipeline_id: str,
    request: CreateConnectionRequest,
    created_by: str,
) -> str:

    pipeline_id = pipeline_id.strip()

    if not pipeline_id:
        raise ValueError(
            "Pipeline ID cannot be empty"
        )

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
        await self.repository.get_by_pipeline_id(
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
        name=request.name,
        pipeline_id=pipeline_id,
        connection_type=request.type,
        host=request.host,
        port=request.port,
        database=request.database,
        username=request.username,
        encrypted_password=encrypted_password,
        created_by=created_by,
    )

    connection_id = (
        await self.repository.create(
            document
        )
    )

    # This is the critical part:
    # assign the newly-created connection as the
    # pipeline's source connection.
    updated = (
        await self.pipeline_repository
        .set_source_connection(
            pipeline_id=pipeline_id,
            connection_id=connection_id,
        )
    )

    if not updated:
        # Best-effort rollback.
        try:
            await self.repository.delete(
                connection_id
            )
        except Exception:
            pass

        raise ValueError(
            "Connection could not be assigned "
            "as the pipeline source"
        )

    return connection_id

