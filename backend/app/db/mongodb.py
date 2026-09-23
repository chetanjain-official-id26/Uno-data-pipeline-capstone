from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import PyMongoError

from app.core.config import get_settings


class MongoDB:
    """Manages application MongoDB connection and lifecycle."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client: AsyncMongoClient | None = None
        self.database = None

    async def connect(self) -> None:
        """Establish connection to MongoDB and verify ping response."""
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
        """Gracefully close the MongoDB client connection."""
        if self.client is not None:
            self.client.close()
            self.client = None
            self.database = None

    def get_collection(self, name: str) -> AsyncCollection:
        """Retrieve a specific collection from the database."""
        if self.database is None:
            raise RuntimeError("MongoDB is not connected")
        return self.database[name]


mongodb = MongoDB()