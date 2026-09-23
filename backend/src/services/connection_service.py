import logging

from src.exceptions.exceptions import AppException
from src.schema.models.connection import build_connection_document
from src.schema.request_response_schema.connection import (
    CreateConnectionRequest,
)
from src.utils.encryption import credential_encryptor

logger = logging.getLogger(__name__)


class ConnectionService:
    """Application/business logic for external connections."""

    def __init__(
        self,
        repository,
        pipeline_repository,
    ) -> None:
        self.repository = repository
        self.pipeline_repository = pipeline_repository

    async def create_connection(
        self,
        pipeline_id: str,
        request: CreateConnectionRequest,
        created_by: str,
    ) -> str:
        # Check that the pipeline exists
        pipeline = await self.pipeline_repository.get_by_id(pipeline_id)

        if pipeline is None:
            raise AppException(
                status_code=404,
                code="PIPELINE_NOT_FOUND",
                message="Pipeline not found",
            )

        try:
            # Encrypt database password
            encrypted_password = credential_encryptor.encrypt(request.password)

            # Build connection document
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

        except Exception as exc:
            logger.exception(
                "Failed to prepare connection configuration: name=%s",
                request.name,
            )

            raise AppException(
                status_code=500,
                code="CONNECTION_CREATE_FAILED",
                message="Failed to create connection configuration",
            ) from exc

        return await self.repository.create(document)