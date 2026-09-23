from dataclasses import dataclass
import re
from urllib.parse import quote_plus

import psycopg
import structlog

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class CockroachDBConfig:
    """Runtime configuration required to connect to CockroachDB."""

    host: str
    port: int
    database: str
    username: str
    password: str


class CockroachDBAdapter:
    """Synchronous CockroachDB adapter."""

    def __init__(
        self,
        config: CockroachDBConfig,
    ) -> None:
        self.config = config

    def _build_connection_url(self) -> str:
        """Build the PostgreSQL connection URL.

        sslmode=require enables TLS encryption without requiring
        a local root certificate file.
        """
        username = quote_plus(self.config.username)
        password = quote_plus(self.config.password)
        database = quote_plus(self.config.database)

        return (
            f"postgresql://{username}:{password}@"
            f"{self.config.host}:{self.config.port}/"
            f"{database}?sslmode=require"
        )

    def _validate_table_name(
        self,
        table_name: str,
    ) -> None:
        """Validate a table name or schema.table name.

        Supported formats:
            users
            public.users
        """
        if not table_name or not table_name.strip():
            raise ValueError("Table name cannot be empty")

        table_name = table_name.strip()
        parts = table_name.split(".")

        if len(parts) > 2:
            raise ValueError(
                "Invalid table name. Use table or schema.table."
            )

        identifier_pattern = r"^[A-Za-z_][A-Za-z0-9_]*$"

        for part in parts:
            if not re.fullmatch(identifier_pattern, part):
                raise ValueError("Invalid table name")

    def _quote_table_name(
        self,
        table_name: str,
    ) -> str:
        """Safely quote a table or schema.table identifier."""
        parts = table_name.strip().split(".")
        return ".".join(f'"{part}"' for part in parts)

    def test_connection(self) -> dict:
        """Test whether the CockroachDB connection works."""
        connection_url = self._build_connection_url()

        try:
            with psycopg.connect(
                connection_url,
                connect_timeout=10,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()

                    if result != (1,):
                        raise RuntimeError(
                            "Database health check failed."
                        )

            logger.info(
                "cockroachdb_connection_successful",
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                username=self.config.username,
            )

            return {
                "status": "success",
                "message": "Connection successful",
            }

        except psycopg.OperationalError as exc:
            logger.exception(
                "cockroachdb_connection_failed",
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                username=self.config.username,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            raise

        except Exception as exc:
            logger.exception(
                "cockroachdb_connection_test_failed",
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                username=self.config.username,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            raise

    def test_table_connection(
        self,
        table_name: str,
        limit: int = 5,
    ) -> dict:
        """Test the connection and fetch sample rows from a table.

        Supports:
            table_name="vehicles"
            table_name="public.vehicles"
        """
        self._validate_table_name(table_name)

        if limit < 1 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")

        connection_url = self._build_connection_url()
        quoted_table_name = self._quote_table_name(table_name)

        try:
            with psycopg.connect(
                connection_url,
                connect_timeout=10,
            ) as connection:
                with connection.cursor() as cursor:
                    # Verify database connection
                    cursor.execute("SELECT 1")
                    cursor.fetchone()

                    # Fetch sample rows
                    query = f"SELECT * FROM {quoted_table_name} LIMIT %s"
                    cursor.execute(query, (limit,))

                    columns = [
                        column.name for column in cursor.description
                    ]
                    rows = cursor.fetchall()

                    logger.info(
                        "cockroachdb_table_query_successful",
                        host=self.config.host,
                        port=self.config.port,
                        database=self.config.database,
                        username=self.config.username,
                        table_name=table_name,
                        row_count=len(rows),
                    )

                    return {
                        "status": "success",
                        "message": (
                            "Connection and table query successful"
                        ),
                        "columns": columns,
                        "rows": [list(row) for row in rows],
                    }

        except psycopg.OperationalError as exc:
            logger.exception(
                "cockroachdb_table_connection_failed",
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                username=self.config.username,
                table_name=table_name,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            raise

        except Exception as exc:
            logger.exception(
                "cockroachdb_table_query_failed",
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                username=self.config.username,
                table_name=table_name,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
            raise