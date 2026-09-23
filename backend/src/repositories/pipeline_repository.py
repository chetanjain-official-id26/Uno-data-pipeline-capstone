from datetime import datetime, timezone

from bson import ObjectId

from database import mongodb


class PipelineRepository:

    def _get_collection(self):
        if mongodb.database is None:
            raise RuntimeError("MongoDB is not connected")

        return mongodb.database["pipelines"]

    async def create(self, data: dict):
        """This is repository layer that connects with db and fetches the data from db and returns the data to service layer."""
        now = datetime.now(timezone.utc)

        data["created_at"] = now
        data["updated_at"] = now
        data["status"] = "draft"

        collection = self._get_collection()

        result = await collection.insert_one(data)

        return str(result.inserted_id)

    async def get_by_id(self, pipeline_id: str):

        collection = self._get_collection()

        try:
            object_id = ObjectId(pipeline_id)
        except Exception:
            return None

        return await collection.find_one(
            {"_id": object_id}
        )

    async def get_all(self):

        collection = self._get_collection()

        cursor = collection.find(
            {}
        ).sort(
            "created_at",
            -1,
        )

        return await cursor.to_list(
            length=None
        )

    async def update(
        self,
        pipeline_id: str,
        data: dict,
    ):

        collection = self._get_collection()

        data["updated_at"] = datetime.now(
            timezone.utc
        )

        try:
            object_id = ObjectId(pipeline_id)
        except Exception:
            return False

        result = await collection.update_one(
            {"_id": object_id},
            {"$set": data},
        )

        return result.modified_count > 0

    async def delete(
        self,
        pipeline_id: str,
    ):

        collection = self._get_collection()

        try:
            object_id = ObjectId(pipeline_id)
        except Exception:
            return False

        result = await collection.delete_one(
            {"_id": object_id}
        )

        return result.deleted_count > 0