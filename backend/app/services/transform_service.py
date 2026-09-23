from bson import ObjectId

from app.db.mongodb import mongodb
from app.execution.preview_executor import PreviewExecutor


class TransformService:

    async def preview(
        self,
        pipeline_id: str,
        target_step_order: int,
    ) -> dict:

        db = mongodb.database

        if db is None:
            raise RuntimeError(
                "MongoDB database is not initialized"
            )

        pipelines = db["pipelines"]
        connections = db["connections"]
        transform_steps = db["transform_steps"]

        pipeline = await pipelines.find_one(
            {"_id": ObjectId(pipeline_id)}
        )

        if pipeline is None:
            raise ValueError(
                "Pipeline not found"
            )

        connection = await connections.find_one(
            {
                "_id": pipeline["source_connection_id"]
            }
        )

        if connection is None:
            raise ValueError(
                "Source connection not found"
            )

        steps_cursor = transform_steps.find(
            {
                "pipeline_id": pipeline_id,
                "step_order": {
                    "$lte": target_step_order
                },
            }
        ).sort(
            "step_order",
            1,
        )

        steps = await steps_cursor.to_list(
            length=None
        )

        executor = PreviewExecutor()

        return executor.preview(
            connection=connection,
            source_table=pipeline["source_table"],
            steps=steps,
            target_step_order=target_step_order,
        )