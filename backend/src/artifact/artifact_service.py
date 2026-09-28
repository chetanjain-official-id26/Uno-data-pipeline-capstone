from typing import Any
from uuid import uuid4

from src.artifact.manifest_builder import ManifestBuilder


class ArtifactService:
    """Builds and uploads pipeline deployment artifacts."""

    def __init__(
        self,
        wheel_builder,
        s3_uploader,
        manifest_builder: ManifestBuilder | None = None,
    ) -> None:
        self.wheel_builder = wheel_builder
        self.s3_uploader = s3_uploader
        self.manifest_builder = (
            manifest_builder
            or ManifestBuilder()
        )

    async def build_and_upload(
        self,
        pipeline_id: str,
        version: int,
        source_connection: dict[str, Any],
        source_table: str,
        transformations: list[dict[str, Any]],
        target: dict[str, Any],
        target_connection: dict[str, Any],
    ) -> dict[str, Any]:
        deployment_id = str(uuid4())

        manifest = self.manifest_builder.build(
            deployment_id=deployment_id,
            pipeline_id=pipeline_id,
            version=version,
            source_connection=source_connection,
            source_table=source_table,
            transformations=transformations,
            target=target,
            target_connection=target_connection,
        )

        wheel_path = self.wheel_builder.build()

        prefix = (
            f"deployments/"
            f"{pipeline_id}/"
            f"{deployment_id}"
        )

        wheel_key = (
            f"{prefix}/pipeline.whl"
        )

        manifest_key = (
            f"{prefix}/manifest.json"
        )

        wheel_uri = await (
            self.s3_uploader.upload_file(
                wheel_path,
                wheel_key,
            )
        )

        manifest_uri = await (
            self.s3_uploader.upload_json(
                manifest,
                manifest_key,
            )
        )

        return {
            "deployment_id": deployment_id,
            "wheel_key": wheel_key,
            "manifest_key": manifest_key,
            "wheel_uri": wheel_uri,
            "manifest_uri": manifest_uri,
            "manifest": manifest,
        }