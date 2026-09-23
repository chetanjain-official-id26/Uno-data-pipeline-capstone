from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    Secrets must never be hard-coded into the source code.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    app_name: str = "DataFlow Hub"
    app_env: str = "development"
    debug: bool = False

    mongodb_uri: str = Field(..., alias="MONGODB_URI")
    mongodb_database: str = Field(..., alias="MONGODB_DATABASE")


    # s3_bucket: str
    # s3_region: str = "ap-south-1"

    # s3_access_key_id: str
    # s3_secret_access_key: str

    # airflow_base_url: str
    # airflow_api_version: str = "v2"
    # airflow_token: str


    credential_encryption_key: str = Field(
        ...,
        alias="CREDENTIAL_ENCRYPTION_KEY",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()