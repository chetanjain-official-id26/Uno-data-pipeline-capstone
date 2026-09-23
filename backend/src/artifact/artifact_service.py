from pathlib import Path

from app.artifact.s3_uploader import S3Uploader
from app.artifact.wheel_builder import WheelBuilder


class ArtifactService:

    def __init__(
        self,
        wheel_builder: WheelBuilder,
        s3_uploader: S3Uploader,
    ):
        self.wheel_builder = wheel_builder
        self.s3_uploader = s3_uploader

    def build_and_upload(
        self,
        pipeline_id: str,
        version: int,
    ):

        wheel_path = (
            self.wheel_builder.build()
        )

        object_key = (
            f"pipelines/"
            f"pipeline_{pipeline_id}/"
            f"{version}/"
            f"{Path(wheel_path).name}"
        )

        s3_uri = self.s3_uploader.upload(
            file_path=str(wheel_path),
            object_key=object_key,
        )

        return {
            "artifact_name": wheel_path.name,
            "artifact_uri": s3_uri,
        }