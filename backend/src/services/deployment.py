import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class DeploymentService:
    """Orchestrates pipeline deployment."""

    def __init__(
        self,
        pipeline_repository,
        connection_repository,
        transformation_repository,
        target_repository,
        deployment_repository,
        artifact_service,
        airflow_service,
    ) -> None:
        self.pipeline_repository = pipeline_repository
        self.connection_repository = connection_repository
        self.transformation_repository = transformation_repository
        self.target_repository = target_repository
        self.deployment_repository = deployment_repository
        self.artifact_service = artifact_service
        self.airflow_service = airflow_service

    async def deploy(
        self,
        pipeline_id: str,
    ) -> dict[str, Any]:
        if not pipeline_id or not pipeline_id.strip():
            raise ValueError("Pipeline ID cannot be empty")

        pipeline_id = pipeline_id.strip()

        # =========================================================
        # 1. LOAD PIPELINE
        # =========================================================

        pipeline = await self.pipeline_repository.get_by_id(pipeline_id)

        if not pipeline:
            raise ValueError("Pipeline not found")

        # =========================================================
        # 2. LOAD SOURCE
        # =========================================================

        source_connection, source_table = await self._load_source(
            pipeline_id=pipeline_id,
            pipeline=pipeline,
        )

        source_connection_id = str(source_connection["_id"])

        # =========================================================
        # 3. LOAD TRANSFORMATIONS
        # =========================================================

        transformations = (
            await self.transformation_repository.get_by_connection(
                source_connection_id
            )
        )

        if transformations is None:
            transformations = []

        # =========================================================
        # 4. LOAD TARGET
        # =========================================================

        target, target_connection = await self._load_target(
            pipeline_id=pipeline_id
        )

        # =========================================================
        # 5. VERSION
        # =========================================================

        latest_version = await self.deployment_repository.get_latest_version(
            pipeline_id
        )

        version = latest_version + 1

        dag_id = f"pipeline_{pipeline_id}"

        deployment_id = None

        try:
            # =====================================================
            # 6. BUILD + UPLOAD ARTIFACT
            # =====================================================

            artifact = await self.artifact_service.build_and_upload(
                pipeline_id=pipeline_id,
                version=version,
                source_connection=source_connection,
                source_table=source_table,
                transformations=transformations,
                target=target,
                target_connection=target_connection,
            )

            deployment_id = artifact["deployment_id"]

            # =====================================================
            # 7. CREATE DEPLOYMENT RECORD
            # =====================================================

            now = datetime.now(timezone.utc)

            deployment_document = {
                "deployment_id": deployment_id,
                "pipeline_id": pipeline_id,
                "version": version,
                "status": "ARTIFACT_CREATED",
                "wheel_key": artifact["wheel_key"],
                "manifest_key": artifact["manifest_key"],
                "wheel_uri": artifact.get("wheel_uri"),
                "manifest_uri": artifact.get("manifest_uri"),
                "dag_id": dag_id,
                "created_at": now,
                "updated_at": now,
            }

            await self.deployment_repository.create(deployment_document)

            # =====================================================
            # 8. DEPLOY AIRFLOW DAG
            # =====================================================

            await self.deployment_repository.update_status(
                deployment_id,
                "AIRFLOW_DEPLOYING",
            )

            await self.airflow_service.deploy_dag(
                dag_id=dag_id,
                pipeline_id=pipeline_id,
                deployment_id=deployment_id,
                wheel_key=artifact["wheel_key"],
                manifest_key=artifact["manifest_key"],
            )

            # =====================================================
            # 9. MARK DEPLOYED
            # =====================================================

            await self.deployment_repository.update_status(
                deployment_id,
                "DEPLOYED",
            )

            deployment = await self.deployment_repository.get_by_id(
                deployment_id
            )

            if deployment:
                return deployment

            deployment_document["status"] = "DEPLOYED"

            return deployment_document

        except Exception as exc:
            logger.exception(
                "pipeline_deployment_failed",
                extra={
                    "pipeline_id": pipeline_id,
                    "deployment_id": deployment_id,
                },
            )

            if deployment_id:
                try:
                    await self.deployment_repository.update_status(
                        deployment_id,
                        "FAILED",
                        error_message=str(exc),
                    )
                except Exception:
                    logger.exception(
                        "failed_to_persist_deployment_failure",
                        extra={
                            "deployment_id": deployment_id,
                        },
                    )

            raise

    # =============================================================
    # SOURCE
    # =============================================================

    async def _load_source(
        self,
        pipeline_id: str,
        pipeline: dict[str, Any],
    ) -> tuple[
        dict[str, Any],
        str,
    ]:
        """Load source connection and source table."""

        source_connection_id = pipeline.get("source_id")

        if not source_connection_id:
            raise ValueError(
                "No source connection is configured for this pipeline"
            )

        source_connection_id = str(source_connection_id).strip()

        if not source_connection_id:
            raise ValueError(
                "No source connection is configured for this pipeline"
            )

        source_connection = await self.connection_repository.get_by_id(
            source_connection_id
        )

        if not source_connection:
            raise ValueError("Source connection not found")

        # Prefer the table saved directly on the pipeline.
        source_table = pipeline.get("source_table")

        # Backward compatibility: older records may only have table_name on the connection.
        if not source_table:
            source_table = source_connection.get("table_name")

        if not source_table:
            raise ValueError(
                "Source table is not configured for this pipeline"
            )

        source_table = str(source_table).strip()

        if not source_table:
            raise ValueError(
                "Source table is not configured for this pipeline"
            )

        # Synchronize old data into pipeline if needed.
        if pipeline.get("source_table") != source_table:
            try:
                await self.pipeline_repository.update(
                    pipeline_id,
                    {
                        "source_id": source_connection_id,
                        "source_table": source_table,
                    },
                )
            except Exception:
                logger.warning(
                    "failed_to_sync_source_fields",
                    extra={
                        "pipeline_id": pipeline_id,
                        "source_connection_id": source_connection_id,
                    },
                )

        return (
            source_connection,
            source_table,
        )

    # =============================================================
    # TARGET
    # =============================================================

    async def _load_target(
        self,
        pipeline_id: str,
    ) -> tuple[
        dict[str, Any],
        dict[str, Any],
    ]:
        """Load target configuration and target connection."""

        target = await self.target_repository.get_by_pipeline(pipeline_id)

        if not target:
            raise ValueError("Target configuration not found")

        target_connection_id = target.get("connection_id")

        if not target_connection_id:
            raise ValueError("Target connection ID is not configured")

        target_connection_id = str(target_connection_id).strip()

        if not target_connection_id:
            raise ValueError("Target connection ID is not configured")

        target_connection = await self.connection_repository.get_by_id(
            target_connection_id
        )

        if not target_connection:
            raise ValueError("Target connection not found")

        target_table = target.get("target_table")

        if not target_table:
            raise ValueError("Target table not configured")

        target_table = str(target_table).strip()

        if not target_table:
            raise ValueError("Target table not configured")

        write_mode = (
            str(
                target.get(
                    "write_mode",
                    "APPEND",
                )
            )
            .strip()
            .upper()
        )

        if write_mode not in {
            "APPEND",
            "OVERWRITE",
        }:
            raise ValueError("Invalid target write mode")

        normalized_target = {
            **target,
            "target_table": target_table,
            "write_mode": write_mode,
        }

        return (
            normalized_target,
            target_connection,
        )