from typing import Any

from bson import ObjectId
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import PyMongoError

from database import mongodb
from src.exceptions.exceptions import DatabaseError


class TransformationRepository:
    """Repository for managing transformation documents."""

    def _get_collection(self) -> AsyncCollection:
        if mongodb.database is None:
            raise RuntimeError("MongoDB is not connected")

        return mongodb.database["transformations"]

    async def create(
        self,
        data: dict[str, Any],
    ) -> str:
        try:
            result = await self._get_collection().insert_one(data)
            return str(result.inserted_id)
        except PyMongoError as exc:
            raise DatabaseError() from exc

    async def get_by_connection(
        self,
        connection_id: str,
    ) -> list[dict[str, Any]]:
        try:
            cursor = (
                self._get_collection()
                .find(
                    {
                        "connection_id": connection_id,
                        "enabled": True,
                    }
                )
                .sort(
                    "step_order",
                    1,
                )
            )

            return await cursor.to_list(length=None)

        except PyMongoError as exc:
            raise DatabaseError() from exc

    async def get_enabled_up_to_step(
        self,
        connection_id: str,
        target_step_order: int,
    ) -> list[dict[str, Any]]:
        try:
            cursor = (
                self._get_collection()
                .find(
                    {
                        "connection_id": connection_id,
                        "enabled": True,
                        "step_order": {
                            "$lte": target_step_order,
                        },
                    }
                )
                .sort(
                    "step_order",
                    1,
                )
            )

            return await cursor.to_list(length=None)

        except PyMongoError as exc:
            raise DatabaseError() from exc

    async def get_step(
        self,
        connection_id: str,
        step_order: int,
    ) -> dict[str, Any] | None:
        try:
            return await self._get_collection().find_one(
                {
                    "connection_id": connection_id,
                    "step_order": step_order,
                    "enabled": True,
                }
            )

        except PyMongoError as exc:
            raise DatabaseError() from exc

    async def update(
        self,
        transformation_id: str,
        data: dict[str, Any],
    ) -> None:
        if not ObjectId.is_valid(transformation_id):
            raise ValueError("Invalid transformation ID")

        try:
            await self._get_collection().update_one(
                {
                    "_id": ObjectId(transformation_id),
                },
                {
                    "$set": data,
                },
            )

        except PyMongoError as exc:
            raise DatabaseError() from exc

    async def delete(
        self,
        transformation_id: str,
    ) -> None:
        if not ObjectId.is_valid(transformation_id):
            raise ValueError("Invalid transformation ID")

        try:
            await self._get_collection().delete_one(
                {
                    "_id": ObjectId(transformation_id),
                }
            )

        except PyMongoError as exc:
            raise DatabaseError() from exc