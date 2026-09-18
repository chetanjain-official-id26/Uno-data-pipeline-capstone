from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

from app.core.config import get_settings


class MongoDB:
    """Manages the application's MongoDB client and database connection."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client: AsyncMongoClient | None = None
        self.database = None

    async def connect(self) -> None:
        """Establish the MongoDB connection and verify connectivity."""
        try:
            self.client = AsyncMongoClient(
                self.settings.mongodb_uri,
                serverSelectionTimeoutMS=5000,
            )

            await self.client.admin.command("ping")

            self.database = self.client[self.settings.mongodb_database]

        except PyMongoError as exc:
            self.client = None
            self.database = None

            raise RuntimeError("Unable to connect to MongoDB") from exc

    async def disconnect(self) -> None:
        """Close the MongoDB client gracefully."""
        if self.client is not None:
            await self.client.close()

            self.client = None
            self.database = None


mongodb = MongoDB()