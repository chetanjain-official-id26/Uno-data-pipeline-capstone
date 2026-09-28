from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo.errors import PyMongoError

from database import mongodb
from src.exceptions.exceptions import DatabaseError


class PipelineRepository:
    """Repository responsible for pipeline persistence."""

    # ============================================================
    # COLLECTION
    # ============================================================

    def _get_collection(self):
        if mongodb.database is None:
            raise RuntimeError("MongoDB is not connected")

        return mongodb.database["pipelines"]

    # ============================================================
    # CREATE
    # ============================================================

    async def create(
        self,
        data: dict[str, Any],
    ) -> str:
        now = datetime.now(timezone.utc)

        document = {
            **data,
            "created_at": now,
            "updated_at": now,
            "status": data.get(
                "status",
                "draft",
            ),
        }

        try:
            result = await self._get_collection().insert_one(document)

            return str(result.inserted_id)

        except PyMongoError as exc:
            raise DatabaseError() from exc

    # ============================================================
    # GET BY ID
    # ============================================================

    async def get_by_id(
        self,
        pipeline_id: str,
    ) -> dict[str, Any] | None:
        if not pipeline_id:
            return None

        pipeline_id = pipeline_id.strip()

        if not ObjectId.is_valid(pipeline_id):
            return None

        try:
            return await self._get_collection().find_one(
                {
                    "_id": ObjectId(pipeline_id),
                }
            )

        except PyMongoError as exc:
            raise DatabaseError() from exc

    # ============================================================
    # GET ALL
    # ============================================================

    async def get_all(
        self,
    ) -> list[dict[str, Any]]:
        try:
            cursor = (
                self._get_collection()
                .find({})
                .sort(
                    "created_at",
                    -1,
                )
            )

            return await cursor.to_list(length=None)

        except PyMongoError as exc:
            raise DatabaseError() from exc

    # ============================================================
    # UPDATE
    # ============================================================

    async def update(
        self,
        pipeline_id: str,
        data: dict[str, Any],
    ) -> bool:
        if not pipeline_id:
            return False

        pipeline_id = pipeline_id.strip()

        if not ObjectId.is_valid(pipeline_id):
            return False

        update_data = {
            **data,
            "updated_at": datetime.now(timezone.utc),
        }

        try:
            result = await self._get_collection().update_one(
                {
                    "_id": ObjectId(pipeline_id),
                },
                {
                    "$set": update_data,
                },
            )

        except PyMongoError as exc:
            raise DatabaseError() from exc

        return result.matched_count > 0

    # ============================================================
    # SET SOURCE CONNECTION
    # ============================================================

    async def set_source_connection(
        self,
        pipeline_id: str,
        connection_id: str,
        source_table: str | None = None,
    ) -> bool:
        if not pipeline_id:
            return False

        if not connection_id:
            return False

        pipeline_id = pipeline_id.strip()
        connection_id = connection_id.strip()

        if not ObjectId.is_valid(pipeline_id):
            return False

        now = datetime.now(timezone.utc)

        update_data: dict[str, Any] = {
            "source_id": connection_id,
            "updated_at": now,
        }

        if source_table is not None:
            source_table = source_table.strip()

            if source_table:
                update_data["source_table"] = source_table

        try:
            result = await self._get_collection().update_one(
                {
                    "_id": ObjectId(pipeline_id),
                },
                {
                    "$set": update_data,
                },
            )

        except PyMongoError as exc:
            raise DatabaseError() from exc

        return result.matched_count > 0

    # ============================================================
    # CLEAR SOURCE CONNECTION
    # ============================================================

    async def clear_source_connection(
        self,
        pipeline_id: str,
    ) -> bool:
        if not pipeline_id:
            return False

        pipeline_id = pipeline_id.strip()

        if not ObjectId.is_valid(pipeline_id):
            return False

        try:
            result = await self._get_collection().update_one(
                {
                    "_id": ObjectId(pipeline_id),
                },
                {
                    "$unset": {
                        "source_id": "",
                        "source_table": "",
                    },
                    "$set": {
                        "updated_at": datetime.now(timezone.utc),
                    },
                },
            )

        except PyMongoError as exc:
            raise DatabaseError() from exc

        return result.matched_count > 0

    # ============================================================
    # DELETE
    # ============================================================

    async def delete(
        self,
        pipeline_id: str,
    ) -> bool:
        if not pipeline_id:
            return False

        pipeline_id = pipeline_id.strip()

        if not ObjectId.is_valid(pipeline_id):
            return False

        try:
            result = await self._get_collection().delete_one(
                {
                    "_id": ObjectId(pipeline_id),
                }
            )

            return result.deleted_count > 0

        except PyMongoError as exc:
            raise DatabaseError() from exc