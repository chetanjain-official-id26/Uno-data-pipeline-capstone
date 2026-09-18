from typing import Any

from bson import ObjectId
from pymongo.errors import PyMongoError

from app.db.mongodb import mongodb


class ConnectionRepository:
    """Handles persistence of connection documents."""

    @property
    def collection(self):
        if mongodb.database is None:
            raise RuntimeError("MongoDB is not initialized")

        return mongodb.database["connections"]

    async def create(
        self,
        document: dict[str, Any],
    ) -> str:
        try:
            result = await self.collection.insert_one(document)

            return str(result.inserted_id)

        except PyMongoError as exc:
            raise RuntimeError("Failed to create connection") from exc

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
            raise RuntimeError("Failed to retrieve connection") from exc