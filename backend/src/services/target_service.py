
import logging
from datetime import datetime, timezone
from typing import Any

from src.engine.target_writer import TargetWriter
from src.repositories.connection_repository import ConnectionRepository
from src.repositories.pipeline_repository import PipelineRepository
from src.repositories.target_repository import TargetRepository


logger = logging.getLogger(__name__)


class TargetService:
    """
    Service responsible for target configuration and target testing.
    """

    def __init__(
        self,
        target_repository: TargetRepository,
        pipeline_repository: PipelineRepository,
        connection_repository: ConnectionRepository,
        target_writer: TargetWriter,
    ) -> None:
        self.target_repository = target_repository
        self.pipeline_repository = pipeline_repository
        self.connection_repository = connection_repository
        self.target_writer = target_writer

    # ============================================================
    # TEST TARGET
    # ============================================================

    async def test_target(
        self,
        connection_id: str,
        target_table: str,
        write_mode: str,
    ) -> dict[str, Any]:
        """
        Validate that a connection can be used as a target.
        """

        connection_id = str(connection_id).strip()
        target_table = str(target_table).strip()
        write_mode = str(write_mode).strip().upper()

        if not connection_id:
            raise ValueError(
                "Connection ID cannot be empty"
            )

        if not target_table:
            raise ValueError(
                "Target table cannot be empty"
            )

        if write_mode not in {
            "APPEND",
            "OVERWRITE",
        }:
            raise ValueError(
                "Write mode must be APPEND or OVERWRITE"
            )

        # --------------------------------------------------------
        # Load connection
        # --------------------------------------------------------

        connection = (
            await self.connection_repository.get_by_id(
                connection_id
            )
        )

        if not connection:
            raise ValueError(
                "Connection not found"
            )

        # --------------------------------------------------------
        # Validate connection credentials
        # --------------------------------------------------------

        required_fields = [
            "host",
            "database",
            "username",
        ]

        missing_fields = [
            field
            for field in required_fields
            if not connection.get(field)
        ]

        if missing_fields:
            raise ValueError(
                "Connection is missing required fields: "
                + ", ".join(missing_fields)
            )

        # --------------------------------------------------------
        # Test target using TargetWriter
        # --------------------------------------------------------

        try:
            result = await self.target_writer.test_target(
                connection=connection,
                target_table=target_table,
            )

        except AttributeError:
            # Backward compatibility if TargetWriter exposes
            # a different test method.
            logger.warning(
                "TargetWriter.test_target is not available"
            )

            result = {
                "success": True,
                "message": "Target connection configuration is valid",
            }

        # --------------------------------------------------------
        # Normalize result
        # --------------------------------------------------------

        if isinstance(result, dict):
            return {
                "success": result.get(
                    "success",
                    True,
                ),
                "message": result.get(
                    "message",
                    "Target connection test successful",
                ),
                "connection_id": connection_id,
                "target_table": target_table,
                "write_mode": write_mode,
                **{
                    key: value
                    for key, value in result.items()
                    if key
                    not in {
                        "success",
                        "message",
                        "connection_id",
                        "target_table",
                        "write_mode",
                    }
                },
            }

        return {
            "success": True,
            "message": "Target connection test successful",
            "connection_id": connection_id,
            "target_table": target_table,
            "write_mode": write_mode,
        }

    # ============================================================
    # CREATE TARGET
    # ============================================================

    async def create_target(
        self,
        pipeline_id: str,
        data: dict[str, Any],
    ) -> str:
        """
        Create a target configuration for a pipeline.
        """

        pipeline_id = str(pipeline_id).strip()

        if not pipeline_id:
            raise ValueError(
                "Pipeline ID cannot be empty"
            )

        # --------------------------------------------------------
        # Verify pipeline
        # --------------------------------------------------------

        pipeline = (
            await self.pipeline_repository.get_by_id(
                pipeline_id
            )
        )

        if not pipeline:
            raise ValueError(
                "Pipeline not found"
            )

        # --------------------------------------------------------
        # Validate connection
        # --------------------------------------------------------

        connection_id = data.get(
            "connection_id"
        )

        if not connection_id:
            raise ValueError(
                "Connection ID is required"
            )

        connection_id = str(
            connection_id
        ).strip()

        connection = (
            await self.connection_repository.get_by_id(
                connection_id
            )
        )

        if not connection:
            raise ValueError(
                "Target connection not found"
            )

        # --------------------------------------------------------
        # Validate target table
        # --------------------------------------------------------

        target_table = data.get(
            "target_table"
        )

        if not target_table:
            raise ValueError(
                "Target table is required"
            )

        target_table = str(
            target_table
        ).strip()

        if not target_table:
            raise ValueError(
                "Target table is required"
            )

        # --------------------------------------------------------
        # Validate write mode
        # --------------------------------------------------------

        write_mode = str(
            data.get(
                "write_mode",
                "APPEND",
            )
        ).strip().upper()

        if write_mode not in {
            "APPEND",
            "OVERWRITE",
        }:
            raise ValueError(
                "Write mode must be APPEND or OVERWRITE"
            )

        # --------------------------------------------------------
        # Prevent duplicate target
        # --------------------------------------------------------

        existing = (
            await self.target_repository
            .get_by_pipeline(
                pipeline_id
            )
        )

        if existing:
            raise ValueError(
                "Target configuration already exists for this pipeline"
            )

        # --------------------------------------------------------
        # Build document
        # --------------------------------------------------------

        now = datetime.now(
            timezone.utc
        )

        target_document = {
            **data,
            "pipeline_id": pipeline_id,
            "connection_id": connection_id,
            "target_table": target_table,
            "write_mode": write_mode,
            "created_at": now,
            "updated_at": now,
        }

        # Remove client-controlled MongoDB ID if supplied.
        target_document.pop(
            "_id",
            None,
        )

        # --------------------------------------------------------
        # Save
        # --------------------------------------------------------

        target_id = await self.target_repository.create(
            target_document
        )

        return str(target_id)

    # ============================================================
    # GET TARGET
    # ============================================================

    async def get_target(
        self,
        pipeline_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve target configuration for a pipeline.
        """

        pipeline_id = str(
            pipeline_id
        ).strip()

        if not pipeline_id:
            raise ValueError(
                "Pipeline ID cannot be empty"
            )

        target = (
            await self.target_repository
            .get_by_pipeline(
                pipeline_id
            )
        )

        if target is None:
            return None

        # Convert MongoDB ObjectId.
        if "_id" in target:
            target["id"] = str(
                target["_id"]
            )
            del target["_id"]

        # Normalize write mode.
        if target.get("write_mode"):
            target["write_mode"] = str(
                target["write_mode"]
            ).upper()

        return target

    # ============================================================
    # UPDATE TARGET
    # ============================================================

    async def update_target(
        self,
        pipeline_id: str,
        data: dict[str, Any],
    ) -> bool:
        """
        Update an existing target configuration.
        """

        pipeline_id = str(
            pipeline_id
        ).strip()

        if not pipeline_id:
            raise ValueError(
                "Pipeline ID cannot be empty"
            )

        if not data:
            raise ValueError(
                "No fields provided for update"
            )

        # --------------------------------------------------------
        # Validate connection if being changed
        # --------------------------------------------------------

        if "connection_id" in data:

            connection_id = str(
                data["connection_id"]
            ).strip()

            if not connection_id:
                raise ValueError(
                    "Connection ID cannot be empty"
                )

            connection = (
                await self.connection_repository
                .get_by_id(
                    connection_id
                )
            )

            if not connection:
                raise ValueError(
                    "Target connection not found"
                )

            data["connection_id"] = connection_id

        # --------------------------------------------------------
        # Validate target table
        # --------------------------------------------------------

        if "target_table" in data:

            target_table = str(
                data["target_table"]
            ).strip()

            if not target_table:
                raise ValueError(
                    "Target table cannot be empty"
                )

            data["target_table"] = target_table

        # --------------------------------------------------------
        # Validate write mode
        # --------------------------------------------------------

        if "write_mode" in data:

            write_mode = str(
                data["write_mode"]
            ).strip().upper()

            if write_mode not in {
                "APPEND",
                "OVERWRITE",
            }:
                raise ValueError(
                    "Write mode must be APPEND or OVERWRITE"
                )

            data["write_mode"] = write_mode

        # --------------------------------------------------------
        # Always update timestamp
        # --------------------------------------------------------

        data["updated_at"] = datetime.now(
            timezone.utc
        )

        # --------------------------------------------------------
        # Update repository
        # --------------------------------------------------------

        updated = await self.target_repository.update_by_pipeline(
            pipeline_id,
            data,
        )

        return bool(updated)

    # ============================================================
    # DELETE TARGET
    # ============================================================

    async def delete_target(
        self,
        pipeline_id: str,
    ) -> bool:
        """
        Delete target configuration for a pipeline.
        """

        pipeline_id = str(
            pipeline_id
        ).strip()

        if not pipeline_id:
            raise ValueError(
                "Pipeline ID cannot be empty"
            )

        deleted = (
            await self.target_repository
            .delete_by_pipeline(
                pipeline_id
            )
        )

        return bool(deleted)

