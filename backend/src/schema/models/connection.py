from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc)


def build_connection_document(
    *,
    name: str,
    pipeline_id: str,
    connection_type: str,
    host: str,
    port: int,
    database: str,
    username: str,
    encrypted_password: str,
    created_by: str,
) -> dict[str, Any]:
    """Build the MongoDB document for an external connection.

    Plaintext credentials must never be persisted.
    """
    now = utc_now()

    return {
        "pipeline_id": pipeline_id,
        "name": name,
        "type": connection_type,
        "config": {
            "host": host,
            "port": port,
            "database": database,
            "username": username,
        },
        "credentials": {
            "password_encrypted": encrypted_password,
        },
        # Lifecycle status of the saved connection.
        "status": "active",
        # Separate from connection status.
        "test": {
            "status": "never_tested",
            "tested_at": None,
            "error_code": None,
        },
        "created_by": created_by,
        "created_at": now,
        "updated_at": now,
    }