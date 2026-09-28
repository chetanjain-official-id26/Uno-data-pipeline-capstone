import logging

from fastapi import APIRouter, status

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
from src.schema.request_response_schema.connection import (
    CreateConnectionRequest,
)
from src.schema.request_response_schema.connectiontest import (
    ConnectionTestRequest,
)
from src.services.connection_service import (
    ConnectionService,
)
from src.services.connection_test_service import (
    ConnectionTestService,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Connections"],
)


# ============================================================
# CREATE CONNECTION
# ============================================================


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
        logger.warning(
            "connection_creation_invalid_pipeline_id"
        )

        raise ConnectionTestError(
            "Pipeline ID cannot be empty.",
            code="INVALID_PIPELINE_ID",
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

        logger.info(
            "connection_created",
            extra={
                "pipeline_id": pipeline_id,
                "connection_id": connection_id,
            },
        )

        return {
            "id": connection_id,
            "message": "Connection created successfully",
        }

    except ValueError as exc:
        logger.warning(
            "connection_creation_validation_failed",
            extra={
                "pipeline_id": pipeline_id,
                "error": str(exc),
            },
        )

        raise ConnectionTestError(
            str(exc),
            code="CONNECTION_CREATION_FAILED",
        ) from exc

    except Exception:
        logger.exception(
            "connection_creation_failed",
            extra={
                "pipeline_id": pipeline_id,
            },
        )

        raise


# ============================================================
# TEST CONNECTION
# ============================================================


@router.post(
    "/connections/{connection_id}/test",
    status_code=status.HTTP_200_OK,
)
async def test_connection(
    connection_id: str,
    request: ConnectionTestRequest,
):
    """Test a stored database connection."""

    if not connection_id.strip():
        logger.warning(
            "connection_test_invalid_connection_id"
        )

        raise ConnectionTestError(
            "Connection ID cannot be empty.",
            code="INVALID_CONNECTION_ID",
        )

    connection_repository = ConnectionRepository()

    service = ConnectionTestService(
        connection_repository=connection_repository,
    )

    try:
        result = await service.test_connection(
            connection_id=connection_id,
            table_name=request.table_name,
            limit=request.limit,
        )

        logger.info(
            "connection_test_succeeded",
            extra={
                "connection_id": connection_id,
                "table_name": request.table_name,
            },
        )

        return result

    except ConnectionNotFoundError:
        logger.warning(
            "connection_test_connection_not_found",
            extra={
                "connection_id": connection_id,
            },
        )

        raise

    except ConnectionTestError:
        logger.warning(
            "connection_test_failed",
            extra={
                "connection_id": connection_id,
                "table_name": request.table_name,
            }
        )

        raise

    except ValueError as exc:
        logger.warning(
            "connection_test_validation_failed",
            extra={
                "connection_id": connection_id,
                "error": str(exc),
            },
        )

        raise ConnectionTestError(
            str(exc),
            code="CONNECTION_TEST_VALIDATION_ERROR",
        ) from exc

    except Exception:
        logger.exception(
            "connection_test_unexpected_error",
            extra={
                "connection_id": connection_id,
                "table_name": request.table_name,
            },
        )

        raise