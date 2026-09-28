import asyncio
from datetime import datetime, timezone

import structlog

from src.exceptions.exceptions import (
ConnectionNotFoundError,
ConnectionTestError,
)
from src.integrations.cockroachdb import (
CockroachDBAdapter,
CockroachDBConfig,
)
from src.repositories.connection_repository import (
ConnectionRepository,
)
from src.repositories.pipeline_repository import (
PipelineRepository,
)
from src.utils.encryption import credential_encryptor

logger = structlog.get_logger(**{"name": "connection_test_service"})

class ConnectionTestService:
 """Business logic for testing stored database connections."""


def __init__(
    self,
    connection_repository: ConnectionRepository,
    pipeline_repository: PipelineRepository | None = None,
) -> None:
    self.connection_repository = connection_repository
    self.pipeline_repository = pipeline_repository

async def test_connection(
    self,
    connection_id: str,
    table_name: str,
    limit: int = 5,
) -> dict:

    if not connection_id or not connection_id.strip():
        raise ValueError(
            "Connection ID cannot be empty."
        )

    if not table_name or not table_name.strip():
        raise ValueError(
            "Table name cannot be empty."
        )

    if limit < 1 or limit > 1000:
        raise ValueError(
            "Limit must be between 1 and 1000."
        )

    return await self._test_cockroachdb(
        connection_id=connection_id.strip(),
        table_name=table_name.strip(),
        limit=limit,
    )

async def _test_cockroachdb(
    self,
    connection_id: str,
    table_name: str,
    limit: int,
) -> dict:

    document = (
        await self.connection_repository
        .get_by_id(connection_id)
    )

    if document is None:
        raise ConnectionNotFoundError()

    config = document.get("config")
    credentials = document.get("credentials")

    if not config:
        raise ConnectionTestError(
            "Connection configuration is missing."
        )

    if not credentials:
        raise ConnectionTestError(
            "Connection credentials are missing."
        )

    encrypted_password = credentials.get(
        "password_encrypted"
    )

    if not encrypted_password:
        raise ConnectionTestError(
            "Encrypted database password is missing."
        )

    try:
        password = credential_encryptor.decrypt(
            encrypted_password
        )
    except Exception as exc:
        logger.exception(
            "database_password_decryption_failed",
            connection_id=connection_id,
        )

        raise ConnectionTestError(
            "Database password could not be decrypted."
        ) from exc

    if not password:
        raise ConnectionTestError(
            "Database password could not be decrypted."
        )

    try:
        adapter = CockroachDBAdapter(
            CockroachDBConfig(
                host=config["host"],
                port=config["port"],
                database=config["database"],
                username=config["username"],
                password=password,
            )
        )

        result = await asyncio.to_thread(
            adapter.test_table_connection,
            table_name,
            limit,
        )

    except Exception as exc:
        logger.exception(
            "cockroachdb_connection_test_failed",
            connection_id=connection_id,
            table_name=table_name,
            error_type=type(exc).__name__,
        )

        tested_at = datetime.now(timezone.utc)

        try:
            await (
                self.connection_repository
                .update_test_result(
                    connection_id,
                    status="failed",
                    tested_at=tested_at,
                    error_code="CONNECTION_TEST_FAILED",
                )
            )
        except Exception:
            logger.exception(
                "failed_to_update_connection_test_result",
                connection_id=connection_id,
            )

        raise ConnectionTestError(
            "Unable to connect to the external database."
        ) from exc

    # Save the table on the connection.
    try:
        await (
            self.connection_repository
            .update_table_name(
                connection_id=connection_id,
                table_name=table_name,
            )
        )
    except Exception as exc:
        logger.exception(
            "failed_to_save_source_table",
            connection_id=connection_id,
            table_name=table_name,
        )

        raise ConnectionTestError(
            "Table was tested successfully, "
            "but the source table could not be saved."
        ) from exc

    # Keep the pipeline source_table synchronized.
    pipeline_id = document.get("pipeline_id")

    if (
        pipeline_id
        and self.pipeline_repository is not None
    ):
        try:
            await (
                self.pipeline_repository
                .update(
                    str(pipeline_id),
                    {
                        "source_id": connection_id,
                        "source_table": table_name,
                    },
                )
            )
        except Exception as exc:
            logger.exception(
                "failed_to_sync_pipeline_source_table",
                connection_id=connection_id,
                pipeline_id=str(pipeline_id),
                table_name=table_name,
            )

            raise ConnectionTestError(
                "Table was tested successfully, "
                "but the pipeline source could not be synchronized."
            ) from exc

    tested_at = datetime.now(
        timezone.utc
    )

    await (
        self.connection_repository
        .update_test_result(
            connection_id,
            status="successful",
            tested_at=tested_at,
            error_code=None,
        )
    )

    rows = result.get("rows", [])
    columns = result.get("columns", [])

    logger.info(
        "cockroachdb_table_query_successful",
        connection_id=connection_id,
        table_name=table_name,
        row_count=len(rows),
    )

    return {
        "connection_id": connection_id,
        "status": "successful",
        "message": (
            "Connection and table query successful"
        ),
        "columns": columns,
        "rows": rows,
        "tested_at": tested_at.isoformat(),
    }

