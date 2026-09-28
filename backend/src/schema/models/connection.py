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
    table_name: str | None = None,
) -> dict[str, Any]:
    """Build the MongoDB document for an external connection.

    Plaintext credentials must never be persisted.
    """
    now = utc_now()

    document: dict[str, Any] = {
        "pipeline_id": pipeline_id,
        "name": name.strip(),
        "type": connection_type.strip(),
        "config": {
            "host": host.strip(),
            "port": port,
            "database": database.strip(),
            "username": username.strip(),
        },
        "credentials": {
            "password_encrypted": encrypted_password,
        },
        "status": "active",
        "test": {
            "status": "never_tested",
            "tested_at": None,
            "error_code": None,
        },
        "created_by": created_by,
        "created_at": now,
        "updated_at": now,
    }

    if table_name:
        document["table_name"] = table_name.strip()

    return document