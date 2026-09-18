from fastapi import APIRouter, HTTPException, status

from app.repositories.connection_repository import (
    ConnectionRepository,
)
from app.schemas.connection import (
    ConnectionResponse,
    CreateConnectionRequest,
)
from app.services.connection_service import ConnectionService

router = APIRouter(
    prefix="/connections",
    tags=["Connections"],
)


@router.post(
    "",
    response_model=ConnectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_connection(
    request: CreateConnectionRequest,
) -> ConnectionResponse:
    try:
        service = ConnectionService(ConnectionRepository())

        connection_id = await service.create_connection(
            request=request,
            created_by="system",
        )

        return ConnectionResponse(
            id=connection_id,
            name=request.name,
            type=request.type,
            host=request.host,
            port=request.port,
            database=request.database,
            username=request.username,
            status="active",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create connection",
        ) from exc