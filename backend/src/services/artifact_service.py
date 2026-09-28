from uuid import uuid4

class ArtifactService:


 def __init__(
    self,
    wheel_builder,
    s3_uploader,
):
    self.wheel_builder = wheel_builder
    self.s3_uploader = s3_uploader

@staticmethod
def _sanitize_connection(
    connection: dict,
) -> dict:

    config = connection.get(
        "config",
        {},
    )

    return {
        "connection_id": str(
            connection.get("_id", "")
        ),
        "name": connection.get(
            "name"
        ),
        "type": connection.get(
            "type"
        ),
        "config": {
            "host": config.get(
                "host"
            ),
            "port": config.get(
                "port"
            ),
            "database": config.get(
                "database"
            ),
            "username": config.get(
                "username"
            ),
        },
    }

async def build_and_upload(
    self,
    pipeline_id: str,
    version: int,
    source_connection: dict,
    source_table: str,
    transformations: list[dict],
    target: dict,
    target_connection: dict,
):

    deployment_id = str(
        uuid4()
    )

    source_manifest_connection = (
        self._sanitize_connection(
            source_connection
        )
    )

    target_manifest_connection = (
        self._sanitize_connection(
            target_connection
        )
    )

    manifest = {
        "deployment_id": deployment_id,

        "pipeline_id": pipeline_id,

        "version": version,

        "source": {
            "connection": (
                source_manifest_connection
            ),
            "table": source_table,
        },

        "transformations": transformations,

        "target": {
            "connection": (
                target_manifest_connection
            ),
            "table": target[
                "target_table"
            ],
            "write_mode": target[
                "write_mode"
            ],
        },
    }

    wheel_path = (
        self.wheel_builder.build()
    )

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

    wheel_uri = (
        await self.s3_uploader.upload_file(
            wheel_path,
            wheel_key,
        )
    )

    manifest_uri = (
        await self.s3_uploader.upload_json(
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

