from typing import Any

from bson import ObjectId
from pymongo.asynchronous.collection import AsyncCollection

from database import mongodb


class TransformationRepository:
    """Repository for managing transformation documents in MongoDB."""

    def __init__(self) -> None:
        self.collection = None

    def _get_collection(self) -> AsyncCollection:
        """Retrieve the transformations collection, ensuring DB is connected."""
        if mongodb.database is None:
            raise RuntimeError("MongoDB is not connected")

        return mongodb.database["transformations"]

    async def create(
        self,
        data: dict[str, Any],
    ) -> str:
        """Create a transformation document."""
        collection = self._get_collection()

        result = await collection.insert_one(data)

        return str(result.inserted_id)

    async def get_by_connection(
        self,
        connection_id: str,
    ) -> list[dict[str, Any]]:
        """Get all enabled transformations for a connection."""
        collection = self._get_collection()

        cursor = collection.find(
            {
                "connection_id": connection_id,
                "enabled": True,
            }
        ).sort("step_order", 1)

        return await cursor.to_list(length=None)

    async def get_step(
        self,
        connection_id: str,
        step_order: int,
    ) -> dict[str, Any] | None:
        """Get a specific enabled transformation step for a connection."""
        collection = self._get_collection()

        return await collection.find_one(
            {
                "connection_id": connection_id,
                "step_order": step_order,
                "enabled": True,
            }
        )

    async def update(
        self,
        transformation_id: str,
        data: dict[str, Any],
    ) -> None:
        """Update a transformation document."""
        collection = self._get_collection()

        await collection.update_one(
            {
                "_id": ObjectId(transformation_id),
            },
            {
                "$set": data,
            },
        )

    async def delete(
        self,
        transformation_id: str,
    ) -> None:
        """Delete a transformation document."""
        collection = self._get_collection()

        await collection.delete_one(
            {
                "_id": ObjectId(transformation_id),
            }
        )