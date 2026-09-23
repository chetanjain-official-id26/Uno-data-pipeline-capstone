from datetime import datetime
from typing import Any

from bson import ObjectId
from pymongo.errors import PyMongoError

from database import mongodb
from src.exceptions.exceptions import (
    ConnectionNotFoundError,
    DatabaseError,
)


class ConnectionRepository:
    """Repository responsible for MongoDB connection persistence."""

    @property
    def collection(self):
        if mongodb.database is None:
            raise RuntimeError("MongoDB database is not initialized")

        return mongodb.database["connections"]

    async def create(
        self,
        document: dict[str, Any],
    ) -> str:
        try:
            result = await self.collection.insert_one(document)
            return str(result.inserted_id)
        except PyMongoError as exc:
            raise DatabaseError() from exc

    async def get_by_id(
        self,
        connection_id: str,
    ) -> dict[str, Any] | None:
        """Get a connection by its MongoDB ObjectId."""
        if not ObjectId.is_valid(connection_id):
            return None

        try:
            return await self.collection.find_one(
                {"_id": ObjectId(connection_id)}
            )
        except PyMongoError as exc:
            raise DatabaseError() from exc

    async def get_by_pipeline_id(
        self,
        pipeline_id: str,
    ) -> dict[str, Any] | None:
        """Get the connection associated with a pipeline.

        The connection document must contain:
            {
                "pipeline_id": "<pipeline-id>"
            }
        """
        if not pipeline_id or not pipeline_id.strip():
            return None

        try:
            return await self.collection.find_one({"pipeline_id": pipeline_id})
        except PyMongoError as exc:
            raise DatabaseError() from exc

    async def get_all_by_pipeline_id(
        self,
        pipeline_id: str,
    ) -> list[dict[str, Any]]:
        """Get all connections associated with a pipeline.

        Useful if a pipeline can have multiple connections.
        """
        if not pipeline_id or not pipeline_id.strip():
            return []

        try:
            cursor = self.collection.find({"pipeline_id": pipeline_id})
            return await cursor.to_list(length=None)
        except PyMongoError as exc:
            raise DatabaseError() from exc

    async def update_test_result(
        self,
        connection_id: str,
        *,
        status: str,
        tested_at: datetime,
        error_code: str | None = None,
    ) -> None:
        """Persist the result of a connection test."""
        if not ObjectId.is_valid(connection_id):
            raise ConnectionNotFoundError()

        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(connection_id)},
                {
                    "$set": {
                        "test.status": status,
                        "test.tested_at": tested_at,
                        "test.error_code": error_code,
                        "updated_at": tested_at,
                    }
                },
            )
        except PyMongoError as exc:
            raise DatabaseError() from exc

        if result.matched_count == 0:
            raise ConnectionNotFoundError()