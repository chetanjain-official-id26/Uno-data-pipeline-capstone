from pymongo import ASCENDING, DESCENDING

from app.db.mongodb import mongodb



async def create_indexes():

    if mongodb.database is None:
        raise RuntimeError("MongoDB is not connected")

    await mongodb.database["pipelines"].create_index(
        "created_at"
    )

    await mongodb.database["transformations"].create_index(
        [
            ("pipeline_id", 1),
            ("step_order", 1),
        ],
        unique=True,
    )

    await mongodb.database["pipeline_targets"].create_index(
        "pipeline_id",
        unique=True,
    )

async def create_indexes() -> None:
    """Create application indexes.

    Index creation is intentionally centralized so that
    database indexing remains explicit and reviewable.
    """

    db = mongodb.database

    if db is None:
        raise RuntimeError("MongoDB database is not initialized")

    connections = db["connections"]

    await connections.create_index(
        [("name", ASCENDING)],
        name="idx_connections_name",
    )

    await connections.create_index(
        [("created_by", ASCENDING)],
        name="idx_connections_created_by",
    )

    await connections.create_index(
        [("status", ASCENDING)],
        name="idx_connections_status",
    )

    await connections.create_index(
        [("created_at", DESCENDING)],
        name="idx_connections_created_at",
    )