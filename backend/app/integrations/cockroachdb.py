from dataclasses import dataclass
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


@dataclass(frozen=True)
class CockroachDBConfig:
    host: str
    port: int
    database: str
    username: str
    password: str


class CockroachDBAdapter:
    """Adapter responsible for communication with CockroachDB.

    Credentials are accepted only in memory and are never logged.
    """

    def __init__(
        self,
        config: CockroachDBConfig,
    ) -> None:
        self.config = config

    def _create_engine(self) -> Engine:
        """Create a short-lived SQLAlchemy engine.

        The password is URL-encoded because it is part of the connection URL.
        """
        username = quote_plus(self.config.username)
        password = quote_plus(self.config.password)
        host = self.config.host
        port = self.config.port
        database = quote_plus(self.config.database)

        url = (
            f"postgresql+psycopg://"
            f"{username}:{password}@"
            f"{host}:{port}/{database}"
            f"?sslmode=require"
        )

        return create_engine(
            url,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=0,
            connect_args={
                "connect_timeout": 5,
            },
        )

    def test_connection(self) -> None:
        """Execute a minimal query to verify connectivity and credentials."""
        engine = self._create_engine()

        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        finally:
            engine.dispose()