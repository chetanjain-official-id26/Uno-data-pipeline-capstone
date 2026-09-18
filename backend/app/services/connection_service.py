from app.core.encryption import credential_encryptor
from app.models.connection import build_connection_document
from app.repositories.connection_repository import (
    ConnectionRepository,
)
from app.schemas.connection import (
    CreateConnectionRequest,
)


class ConnectionService:
    """Application/business logic for external connections."""

    def __init__(
        self,
        repository: ConnectionRepository,
    ) -> None:
        self.repository = repository

    async def create_connection(
        self,
        request: CreateConnectionRequest,
        created_by: str,
    ) -> str:
        encrypted_password = credential_encryptor.encrypt(
            request.password
        )

        document = build_connection_document(
            name=request.name,
            connection_type=request.type,
            host=request.host,
            port=request.port,
            database=request.database,
            username=request.username,
            encrypted_password=encrypted_password,
            created_by=created_by,
        )

        return await self.repository.create(document)