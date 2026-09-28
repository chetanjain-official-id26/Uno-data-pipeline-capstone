from datetime import datetime, timezone
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
        raise RuntimeError(
            "MongoDB database is not initialized"
        )

    return mongodb.database["connections"]

async def create(
    self,
    document: dict[str, Any],
) -> str:
    try:
        result = await self.collection.insert_one(
            document
        )

        return str(result.inserted_id)

    except PyMongoError as exc:
        raise DatabaseError() from exc

async def get_by_id(
    self,
    connection_id: str,
) -> dict[str, Any] | None:

    if not connection_id:
        return None

    connection_id = connection_id.strip()

    if not ObjectId.is_valid(connection_id):
        return None

    try:
        return await self.collection.find_one(
            {
                "_id": ObjectId(connection_id)
            }
        )

    except PyMongoError as exc:
        raise DatabaseError() from exc

async def get_by_pipeline_id(
    self,
    pipeline_id: str,
) -> dict[str, Any] | None:

    if not pipeline_id or not pipeline_id.strip():
        return None

    pipeline_id = pipeline_id.strip()

    try:
        queries = [
            {
                "pipeline_id": pipeline_id,
            }
        ]

        if ObjectId.is_valid(pipeline_id):
            queries.append(
                {
                    "pipeline_id": ObjectId(
                        pipeline_id
                    ),
                }
            )

        return await self.collection.find_one(
            {
                "$or": queries,
            }
        )

    except PyMongoError as exc:
        raise DatabaseError() from exc

async def get_all_by_pipeline_id(
    self,
    pipeline_id: str,
) -> list[dict[str, Any]]:

    if not pipeline_id or not pipeline_id.strip():
        return []

    pipeline_id = pipeline_id.strip()

    try:
        queries = [
            {
                "pipeline_id": pipeline_id,
            }
        ]

        if ObjectId.is_valid(pipeline_id):
            queries.append(
                {
                    "pipeline_id": ObjectId(
                        pipeline_id
                    ),
                }
            )

        cursor = self.collection.find(
            {
                "$or": queries,
            }
        )

        return await cursor.to_list(
            length=None
        )

    except PyMongoError as exc:
        raise DatabaseError() from exc

async def update(
    self,
    connection_id: str,
    data: dict[str, Any],
) -> bool:

    if not ObjectId.is_valid(connection_id):
        return False

    update_data = {
        **data,
        "updated_at": datetime.now(
            timezone.utc
        ),
    }

    try:
        result = await self.collection.update_one(
            {
                "_id": ObjectId(connection_id)
            },
            {
                "$set": update_data,
            },
        )

    except PyMongoError as exc:
        raise DatabaseError() from exc

    return result.matched_count > 0

async def update_table_name(
    self,
    connection_id: str,
    table_name: str,
) -> None:

    if not ObjectId.is_valid(connection_id):
        raise ConnectionNotFoundError()

    if not table_name or not table_name.strip():
        raise ValueError(
            "Table name cannot be empty"
        )

    now = datetime.now(timezone.utc)

    try:
        result = await self.collection.update_one(
            {
                "_id": ObjectId(connection_id)
            },
            {
                "$set": {
                    "table_name": table_name.strip(),
                    "updated_at": now,
                }
            },
        )

    except PyMongoError as exc:
        raise DatabaseError() from exc

    if result.matched_count == 0:
        raise ConnectionNotFoundError()

async def update_test_result(
    self,
    connection_id: str,
    *,
    status: str,
    tested_at: datetime,
    error_code: str | None = None,
) -> None:

    if not ObjectId.is_valid(connection_id):
        raise ConnectionNotFoundError()

    try:
        result = await self.collection.update_one(
            {
                "_id": ObjectId(connection_id)
            },
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

async def delete(
    self,
    connection_id: str,
) -> bool:

    if not ObjectId.is_valid(connection_id):
        return False

    try:
        result = await self.collection.delete_one(
            {
                "_id": ObjectId(connection_id)
            }
        )

    except PyMongoError as exc:
        raise DatabaseError() from exc

    return result.deleted_count > 0

