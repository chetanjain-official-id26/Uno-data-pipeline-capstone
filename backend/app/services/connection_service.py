import logging

from src.utlis.encryption import credential_encryptor
from src.exceptions.exceptions import AppException
from src.schema.models.connection import build_connection_document
from src.repositories.connection_repository import ConnectionRepository
from src.schema.request_response_schema.connection import CreateConnectionRequest


logger = logging.getLogger(__name__)


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

        try:
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

        except Exception as exc:
            logger.exception(
                "Failed to prepare connection configuration: name=%s",
                request.name,
            )

            raise AppException(
                status_code=500,
                message="Failed to create connection configuration",
            ) from exc

        return await self.repository.create(document)