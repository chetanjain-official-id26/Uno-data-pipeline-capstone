from datetime import datetime, timezone

from bson import ObjectId

from app.db.mongodb import mongodb


class TargetRepository:

    def _get_collection(self):
        if mongodb.database is None:
            raise RuntimeError("MongoDB is not connected")

        return mongodb.database["pipeline_targets"]

    async def create(
        self,
        pipeline_id: str,
        data: dict,
    ) -> str:

        collection = self._get_collection()

        existing = await collection.find_one(
            {
                "pipeline_id": pipeline_id,
            }
        )

        if existing:
            raise ValueError(
                "Target configuration already exists for this pipeline"
            )

        now = datetime.now(timezone.utc)

        document = {
            "pipeline_id": pipeline_id,
            "connection_id": data["connection_id"],
            "target_table": data["target_table"],
            "write_mode": data["write_mode"],
            "created_at": now,
            "updated_at": now,
        }

        result = await collection.insert_one(document)

        return str(result.inserted_id)

    async def get_by_pipeline(
        self,
        pipeline_id: str,
    ):
        collection = self._get_collection()

        return await collection.find_one(
            {
                "pipeline_id": pipeline_id,
            }
        )

    async def update(
        self,
        pipeline_id: str,
        data: dict,
    ) -> bool:

        collection = self._get_collection()

        data["updated_at"] = datetime.now(timezone.utc)

        result = await collection.update_one(
            {
                "pipeline_id": pipeline_id,
            },
            {
                "$set": data,
            },
        )

        return result.matched_count > 0

    async def delete(
        self,
        pipeline_id: str,
    ) -> bool:

        collection = self._get_collection()

        result = await collection.delete_one(
            {
                "pipeline_id": pipeline_id,
            }
        )

        return result.deleted_count > 0