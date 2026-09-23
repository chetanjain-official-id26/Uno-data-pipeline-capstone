import asyncio
import hashlib
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
from src.utils.encryption import credential_encryptor

logger = structlog.get_logger(__name__)


class ConnectionTestService:
    """Business logic for testing stored external database connections."""

    def __init__(
        self,
        connection_repository: ConnectionRepository,
    ) -> None:
        self.connection_repository = connection_repository

    async def test_connection(
        self,
        connection_id: str,
        table_name: str,
        limit: int = 5,
    ) -> dict:
        """Test a stored database connection and return sample rows."""
        if not connection_id or not connection_id.strip():
            raise ValueError("Connection ID cannot be empty.")

        if not table_name or not table_name.strip():
            raise ValueError("Table name cannot be empty.")

        if limit < 1 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000.")

        return await self.test_cockroachdb(
            connection_id=connection_id,
            table_name=table_name,
            limit=limit,
        )

    async def test_cockroachdb(
        self,
        connection_id: str,
        table_name: str,
        limit: int = 5,
    ) -> dict:
        """Test CockroachDB connection and fetch sample rows."""
        document = await self.connection_repository.get_by_id(
            connection_id
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

        try:
            encrypted_password = credentials.get("password_encrypted")

            if not encrypted_password:
                raise ConnectionTestError(
                    "Encrypted database password is missing."
                )

            password = credential_encryptor.decrypt(encrypted_password)

            if not password:
                raise ConnectionTestError(
                    "Database password could not be decrypted."
                )

            # Temporary debugging fingerprint.
            # Does not expose the actual password.
            password_fingerprint = hashlib.sha256(
                password.encode("utf-8")
            ).hexdigest()[:12]

            logger.info(
                "cockroachdb_credentials_loaded",
                connection_id=connection_id,
                host=config.get("host"),
                port=config.get("port"),
                database=config.get("database"),
                username=config.get("username"),
                password_length=len(password),
                password_fingerprint=password_fingerprint,
            )

            adapter = CockroachDBAdapter(
                CockroachDBConfig(
                    host=config["host"],
                    port=config["port"],
                    database=config["database"],
                    username=config["username"],
                    password=password,
                )
            )

            # Connect to CockroachDB and fetch sample rows.
            result = await asyncio.to_thread(
                adapter.test_table_connection,
                table_name,
                limit,
            )

        except ConnectionTestError:
            raise

        except Exception as exc:
            logger.exception(
                "cockroachdb_connection_test_failed",
                connection_id=connection_id,
                table_name=table_name,
                error_type=type(exc).__name__,
            )

            tested_at = datetime.now(timezone.utc)

            try:
                await self.connection_repository.update_test_result(
                    connection_id,
                    status="failed",
                    tested_at=tested_at,
                    error_code="CONNECTION_TEST_FAILED",
                )
            except Exception:
                logger.exception(
                    "failed_to_update_connection_test_result",
                    connection_id=connection_id,
                )

            raise ConnectionTestError(
                "Unable to connect to the external database."
            ) from exc

        tested_at = datetime.now(timezone.utc)

        await self.connection_repository.update_test_result(
            connection_id,
            status="successful",
            tested_at=tested_at,
            error_code=None,
        )

        logger.info(
            "cockroachdb_table_query_successful",
            connection_id=connection_id,
            table_name=table_name,
            row_count=len(result["rows"]),
        )

        return {
            "connection_id": connection_id,
            "status": "successful",
            "message": "Connection and table query successful",
            "columns": result["columns"],
            "rows": result["rows"],
            "tested_at": tested_at.isoformat(),
        }