from pathlib import Path

import boto3

from app.core.config import get_settings


class S3Uploader:

    def __init__(self):

        settings = get_settings()

        self.bucket = settings.s3_bucket

        self.client = boto3.client(
            "s3",
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
        )

    def upload(
        self,
        file_path: str,
        object_key: str,
    ) -> str:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Artifact not found: {file_path}"
            )

        self.client.upload_file(
            str(path),
            self.bucket,
            object_key,
        )

        return (
            f"s3://{self.bucket}/{object_key}"
        )