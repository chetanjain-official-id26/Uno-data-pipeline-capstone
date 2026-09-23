from datetime import datetime
from typing import Any

from bson import ObjectId
from pymongo.errors import PyMongoError

from app.core.exceptions import (ConnectionNotFoundError, DatabaseError,)
from app.db.mongodb import mongodb


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
        if not ObjectId.is_valid(connection_id):
            return None

        try:
            return await self.collection.find_one(
                {"_id": ObjectId(connection_id)}
            )

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

        if result.matched_count == 0:
            raise ConnectionNotFoundError()