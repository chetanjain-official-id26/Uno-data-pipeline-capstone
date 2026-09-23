from fastapi import APIRouter, HTTPException, status

from src.exceptions.exceptions import (
    ConnectionNotFoundError,
    ConnectionTestError,
)
from src.repositories.connection_repository import (
    ConnectionRepository,
)
from src.repositories.pipeline_repository import (
    PipelineRepository,
)
from src.schema.request_response_schema.connectiontest import (
    ConnectionTestRequest,
    
)
from src.schema.request_response_schema.connection import (
    CreateConnectionRequest,)
from src.services.connection_service import (
    ConnectionService,
)
from src.services.connection_test_service import (
    ConnectionTestService,
)

router = APIRouter(
    tags=["Connections"],
)


@router.post(
    "/pipelines/{pipeline_id}/connection",
    status_code=status.HTTP_201_CREATED,
)
async def create_connection(
    pipeline_id: str,
    request: CreateConnectionRequest,
):
    """Create a database connection for a pipeline."""
    if not pipeline_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline ID cannot be empty",
        )

    repository = ConnectionRepository()
    pipeline_repository = PipelineRepository()

    service = ConnectionService(
        repository=repository,
        pipeline_repository=pipeline_repository,
    )

    try:
        connection_id = await service.create_connection(
            pipeline_id=pipeline_id,
            request=request,
            created_by="system",
        )

        return {
            "id": connection_id,
            "message": "Connection created successfully",
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/connections/{connection_id}/test",
    status_code=status.HTTP_200_OK,
)
async def test_connection(
    connection_id: str,
    request: ConnectionTestRequest,
):
    """Test a stored database connection and return sample rows."""
    if not connection_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection ID cannot be empty",
        )

    connection_repository = ConnectionRepository()

    service = ConnectionTestService(
        connection_repository=connection_repository,
    )

    try:
        return await service.test_connection(
            connection_id=connection_id,
            table_name=request.table_name,
            limit=request.limit,
        )

    except ConnectionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found.",
        )

    except ConnectionTestError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc