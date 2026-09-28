import asyncio
import json
from pathlib import Path
from typing import Any

import boto3


class S3Uploader:
    """Uploads deployment artifacts to S3."""

    def __init__(
        self,
        bucket: str,
        region: str | None = None,
    ) -> None:
        if not bucket:
            raise ValueError(
                "S3 bucket is required"
            )

        self.bucket = bucket

        self.client = boto3.client(
            "s3",
            region_name=region,
        )

    async def upload_file(
        self,
        file_path: str | Path,
        key: str,
    ) -> str:
        file_path = Path(
            file_path
        )

        if not file_path.exists():
            raise FileNotFoundError(
                f"Artifact not found: {file_path}"
            )

        if not file_path.is_file():
            raise ValueError(
                f"Artifact path is not a file: {file_path}"
            )

        await asyncio.to_thread(
            self.client.upload_file,
            str(file_path),
            self.bucket,
            key,
        )

        return (
            f"s3://{self.bucket}/{key}"
        )

    async def upload_json(
        self,
        data: dict[str, Any],
        key: str,
    ) -> str:
        body = json.dumps(
            data,
            indent=2,
            default=str,
        )

        await asyncio.to_thread(
            self.client.put_object,
            Bucket=self.bucket,
            Key=key,
            Body=body.encode("utf-8"),
            ContentType="application/json",
        )

        return (
            f"s3://{self.bucket}/{key}"
        )