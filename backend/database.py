from pymongo import ASCENDING, DESCENDING, AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import PyMongoError

from core.config import get_settings


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

            self.database = self.client[
                self.settings.mongodb_database
            ]

        except PyMongoError as exc:
            self.client = None
            self.database = None

            raise RuntimeError(
                "Unable to connect to MongoDB"
            ) from exc

    async def disconnect(self) -> None:
        """Gracefully close the MongoDB client connection."""

        if self.client is not None:
            self.client.close()
            self.client = None
            self.database = None

    def get_collection(
        self,
        name: str,
    ) -> AsyncCollection:
        """Retrieve a specific collection from MongoDB."""

        if self.database is None:
            raise RuntimeError(
                "MongoDB is not connected"
            )

        return self.database[name]


mongodb = MongoDB()


async def create_indexes() -> None:
    """Create application MongoDB indexes."""

    db = mongodb.database

    if db is None:
        raise RuntimeError(
            "MongoDB database is not initialized"
        )

    # -----------------------------------------
    # Connections
    # -----------------------------------------

    connections = db["connections"]

    await connections.create_index(
        [("name", ASCENDING)],
        name="idx_connections_name",
    )

    await connections.create_index(
        [("created_by", ASCENDING)],
        name="idx_connections_created_by",
    )

    await connections.create_index(
        [("status", ASCENDING)],
        name="idx_connections_status",
    )

    await connections.create_index(
        [("created_at", DESCENDING)],
        name="idx_connections_created_at",
    )

    # -----------------------------------------
    # Pipelines
    # -----------------------------------------

    pipelines = db["pipelines"]

    await pipelines.create_index(
        [("created_at", DESCENDING)],
        name="idx_pipelines_created_at",
    )

    # -----------------------------------------
    # Transformations
    # -----------------------------------------

    transformations = db["transformations"]

    await transformations.create_index(
        [
            ("pipeline_id", ASCENDING),
            ("step_order", ASCENDING),
        ],
        unique=True,
        name="idx_transformations_pipeline_step",
    )

    # -----------------------------------------
    # Pipeline Targets
    # -----------------------------------------

    pipeline_targets = db["pipeline_targets"]

    await pipeline_targets.create_index(
        [("pipeline_id", ASCENDING)],
        unique=True,
        name="idx_pipeline_targets_pipeline",
    )