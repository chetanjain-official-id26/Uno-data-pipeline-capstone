import asyncio
import hashlib
from datetime import datetime, timezone

import structlog

from app.core.encryption import credential_encryptor
from app.core.exceptions import (
    ConnectionNotFoundError,
    ConnectionTestError,
)
from app.integrations.cockroachdb import (
    CockroachDBAdapter,
    CockroachDBConfig,
)
from app.repositories.connection_repository import (
    ConnectionRepository,
)

logger = structlog.get_logger(__name__)


class ConnectionTestService:
    """Business logic for testing stored external database connections.

    The CockroachDB adapter uses synchronous SQLAlchemy I/O.
    The blocking operation is therefore executed in a worker thread
    so the FastAPI event loop remains responsive.
    """

    def __init__(
        self,
        repository: ConnectionRepository,
    ) -> None:
        self.repository = repository

    async def test_cockroachdb(
        self,
        connection_id: str,
    ) -> dict:
        """Test a stored CockroachDB connection."""
        document = await self.repository.get_by_id(connection_id)

        if document is None:
            raise ConnectionNotFoundError()

        config = document.get("config")
        credentials = document.get("credentials")

        if not config or not credentials:
            raise ConnectionTestError(
                "Connection configuration or credentials are missing."
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
            # This does NOT expose the actual password.
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

            # SQLAlchemy is synchronous, so execute it outside
            # the FastAPI event loop.
            await asyncio.to_thread(adapter.test_connection)

        except ConnectionTestError:
            raise

        except Exception as exc:
            logger.exception(
                "cockroachdb_connection_test_failed",
                connection_id=connection_id,
                error_type=type(exc).__name__,
            )

            tested_at = datetime.now(timezone.utc)

            await self.repository.update_test_result(
                connection_id,
                status="failed",
                tested_at=tested_at,
                error_code="CONNECTION_TEST_FAILED",
            )

            raise ConnectionTestError(
                "Unable to connect to the external database."
            ) from exc

        tested_at = datetime.now(timezone.utc)

        await self.repository.update_test_result(
            connection_id,
            status="successful",
            tested_at=tested_at,
            error_code=None,
        )

        logger.info(
            "cockroachdb_connection_test_successful",
            connection_id=connection_id,
        )

        return {
            "connection_id": connection_id,
            "status": "successful",
            "tested_at": tested_at.isoformat(),
        }