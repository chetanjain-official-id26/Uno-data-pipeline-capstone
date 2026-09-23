from dataclasses import dataclass
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
    """Synchronous CockroachDB adapter.

    Uses psycopg directly because CockroachDB may return
    a server version string that SQLAlchemy's PostgreSQL
    dialect cannot parse correctly.
    """

    def __init__(self, config: CockroachDBConfig) -> None:
        self.config = config

    def _build_connection_url(self) -> str:
        """Build the CockroachDB PostgreSQL connection URL."""
        username = quote_plus(self.config.username)
        password = quote_plus(self.config.password)
        database = quote_plus(self.config.database)

        return (
            f"postgresql://{username}:{password}@"
            f"{self.config.host}:{self.config.port}/{database}"
            "?sslmode=require"
        )

    def test_connection(self) -> None:
        """Test CockroachDB connectivity."""
        connection_url = self._build_connection_url()

        try:
            with psycopg.connect(
                connection_url,
                connect_timeout=10,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
        except Exception:
            logger.exception(
                "cockroachdb_connection_failed",
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                username=self.config.username,
            ) 
            raise