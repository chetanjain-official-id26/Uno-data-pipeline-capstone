from bson import ObjectId

from database import mongodb
from src.execution.preview_executor import PreviewExecutor


class TransformService:
    async def preview(
        self,
        connection_id: str,
        target_step_order: int,
    ) -> dict:
        """Preview transformations for a database connection.

        The connection ID is the source of truth. The service retrieves
        the connection and its transformation steps directly without
        requiring a pipeline ID.
        """
        db = mongodb.database

        if db is None:
            raise RuntimeError("MongoDB database is not initialized")

        connections = db["connections"]
        transformations = db["transformations"]

        # Validate connection ID.
        if not connection_id or not connection_id.strip():
            raise ValueError("Connection ID cannot be empty")

        if not ObjectId.is_valid(connection_id):
            raise ValueError("Invalid connection ID")

        # Find the stored connection.
        connection = await connections.find_one(
            {
                "_id": ObjectId(connection_id),
            }
        )

        if connection is None:
            raise ValueError("Connection not found")

        # Find transformation steps belonging to this connection.
        steps_cursor = transformations.find(
            {
                "connection_id": connection_id,
                "enabled": True,
                "step_order": {
                    "$lte": target_step_order,
                },
            }
        ).sort("step_order", 1)

        steps = await steps_cursor.to_list(length=None)

        if not steps:
            raise ValueError(
                "No transformation steps found for this connection"
            )

        # Source table should come from the connection configuration.
        config = connection.get("config")

        if not config:
            raise ValueError("Connection configuration is missing")

        source_table = config.get("table_name") or config.get("source_table")

        if not source_table:
            raise ValueError(
                "Source table is missing from connection configuration"
            )

        executor = PreviewExecutor()

        return executor.preview(
            connection=connection,
            source_table=source_table,
            steps=steps,
            target_step_order=target_step_order,
        )