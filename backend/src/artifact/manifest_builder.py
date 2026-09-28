from typing import Any


class ManifestBuilder:
    """Builds the deployment manifest consumed by the runtime."""

    def build(
        self,
        *,
        deployment_id: str,
        pipeline_id: str,
        version: int,
        source_connection: dict[str, Any],
        source_table: str,
        transformations: list[dict[str, Any]],
        target: dict[str, Any],
        target_connection: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "deployment_id": deployment_id,
            "pipeline_id": pipeline_id,
            "version": version,
            "source": {
                "connection": source_connection,
                "table": source_table,
            },
            "transformations": transformations,
            "target": {
                "connection": target_connection,
                "table": target["target_table"],
                "write_mode": target.get(
                    "write_mode",
                    "APPEND",
                ),
            },
        }