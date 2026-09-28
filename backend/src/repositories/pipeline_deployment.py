from datetime import datetime, timezone
from typing import Any

from pymongo.errors import PyMongoError

from database import mongodb
from src.exceptions.exceptions import DatabaseError

class DeploymentRepository:
 """Repository for pipeline deployment persistence."""


def _get_collection(self):
    if mongodb.database is None:
        raise RuntimeError(
            "MongoDB is not connected"
        )

    return mongodb.database[
        "pipeline_deployments"
    ]

async def create(
    self,
    data: dict[str, Any],
) -> str:

    now = datetime.now(timezone.utc)

    document = {
        **data,
        "created_at": data.get(
            "created_at",
            now,
        ),
        "updated_at": data.get(
            "updated_at",
            now,
        ),
    }

    try:
        result = (
            await self._get_collection()
            .insert_one(
                document
            )
        )

        return str(result.inserted_id)

    except PyMongoError as exc:
        raise DatabaseError() from exc

async def get_by_id(
    self,
    deployment_id: str,
) -> dict[str, Any] | None:

    try:
        return (
            await self._get_collection()
            .find_one(
                {
                    "deployment_id": deployment_id,
                }
            )
        )

    except PyMongoError as exc:
        raise DatabaseError() from exc

async def get_active_by_pipeline(
    self,
    pipeline_id: str,
) -> dict[str, Any] | None:

    try:
        return (
            await self._get_collection()
            .find_one(
                {
                    "pipeline_id": pipeline_id,
                    "status": "DEPLOYED",
                },
                sort=[
                    ("version", -1)
                ],
            )
        )

    except PyMongoError as exc:
        raise DatabaseError() from exc

async def get_latest_version(
    self,
    pipeline_id: str,
) -> int:

    try:
        deployment = (
            await self._get_collection()
            .find_one(
                {
                    "pipeline_id": pipeline_id,
                },
                sort=[
                    ("version", -1)
                ],
            )
        )

    except PyMongoError as exc:
        raise DatabaseError() from exc

    if not deployment:
        return 0

    return int(
        deployment.get(
            "version",
            0,
        )
    )

async def update_status(
    self,
    deployment_id: str,
    status: str,
    error_message: str | None = None,
) -> bool:

    now = datetime.now(
        timezone.utc
    )

    update: dict[str, Any] = {
        "status": status,
        "updated_at": now,
    }

    if status == "FAILED":
        update["error_message"] = (
            error_message
        )
    else:
        update["error_message"] = None

    try:
        result = (
            await self._get_collection()
            .update_one(
                {
                    "deployment_id": deployment_id,
                },
                {
                    "$set": update,
                },
            )
        )

    except PyMongoError as exc:
        raise DatabaseError() from exc

    return result.matched_count > 0

