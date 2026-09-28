from datetime import datetime, timezone
from typing import Any

from pymongo.errors import PyMongoError

from database import mongodb
from src.exceptions.exceptions import DatabaseError

class TargetRepository:
 """Repository responsible for pipeline target persistence."""


def _get_collection(self):
    if mongodb.database is None:
        raise RuntimeError(
            "MongoDB is not connected"
        )

    return mongodb.database[
        "pipeline_targets"
    ]

async def create(
    self,
    pipeline_id: str,
    data: dict[str, Any],
) -> str:

    collection = self._get_collection()

    try:
        existing = await collection.find_one(
            {
                "pipeline_id": pipeline_id,
            }
        )

        if existing:
            raise ValueError(
                "Target configuration already exists "
                "for this pipeline"
            )

        now = datetime.now(
            timezone.utc
        )

        document = {
            "pipeline_id": pipeline_id,
            "connection_id": str(
                data["connection_id"]
            ),
            "target_table": str(
                data["target_table"]
            ).strip(),
            "write_mode": str(
                data.get(
                    "write_mode",
                    "APPEND",
                )
            ).upper(),
            "created_at": now,
            "updated_at": now,
        }

        result = await collection.insert_one(
            document
        )

        return str(
            result.inserted_id
        )

    except ValueError:
        raise

    except PyMongoError as exc:
        raise DatabaseError() from exc

async def get_by_pipeline(
    self,
    pipeline_id: str,
) -> dict[str, Any] | None:

    try:
        return await self._get_collection().find_one(
            {
                "pipeline_id": pipeline_id,
            }
        )

    except PyMongoError as exc:
        raise DatabaseError() from exc

async def get_by_connection_id(
    self,
    connection_id: str,
) -> dict[str, Any] | None:

    try:
        return await self._get_collection().find_one(
            {
                "connection_id": connection_id,
            }
        )

    except PyMongoError as exc:
        raise DatabaseError() from exc

async def update(
    self,
    pipeline_id: str,
    data: dict[str, Any],
) -> bool:

    update_data = {
        **data,
        "updated_at": datetime.now(
            timezone.utc
        ),
    }

    try:
        result = (
            await self._get_collection()
            .update_one(
                {
                    "pipeline_id": pipeline_id,
                },
                {
                    "$set": update_data,
                },
            )
        )

    except PyMongoError as exc:
        raise DatabaseError() from exc

    return result.matched_count > 0

async def delete(
    self,
    pipeline_id: str,
) -> bool:

    try:
        result = (
            await self._get_collection()
            .delete_one(
                {
                    "pipeline_id": pipeline_id,
                }
            )
        )

    except PyMongoError as exc:
        raise DatabaseError() from exc

    return result.deleted_count > 0

