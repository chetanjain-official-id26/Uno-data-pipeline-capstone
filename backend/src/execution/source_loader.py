from typing import Any

from pyspark.sql import DataFrame, SparkSession

from src.utils.encryption import credential_encryptor


def load_sample_from_cockroach(
    *,
    spark: SparkSession,
    connection: dict[str, Any],
    table_name: str,
    limit: int = 100,
) -> DataFrame:
    """Load a sample of source data from CockroachDB using Spark JDBC."""
    if not table_name:
        raise ValueError("Source table cannot be empty")

    config = connection.get("config")
    if not config:
        raise ValueError("Connection configuration is missing")

    credentials = connection.get("credentials")
    if not credentials:
        raise ValueError("Connection credentials are missing")

    host = config.get("host")
    port = config.get("port")
    database = config.get("database")
    username = config.get("username")
    encrypted_password = credentials.get("password_encrypted")

    if not host:
        raise ValueError("Connection host is missing")

    if not port:
        raise ValueError("Connection port is missing")

    if not database:
        raise ValueError("Connection database is missing")

    if not username:
        raise ValueError("Connection username is missing")

    if not encrypted_password:
        raise ValueError("Encrypted password is missing")

    password = credential_encryptor.decrypt(encrypted_password)
    if not password:
        raise ValueError("Unable to decrypt database password")

    # -----------------------------------------------
    # Validate limit
    # -----------------------------------------------
    if limit < 1:
        limit = 100

    # -----------------------------------------------
    # JDBC URL
    # -----------------------------------------------
    jdbc_url = f"jdbc:postgresql://{host}:{port}/{database}?sslmode=require"

    # -----------------------------------------------
    # Source query
    # -----------------------------------------------
    query = f"(SELECT * FROM {table_name} LIMIT {int(limit)}) AS source_data"

    # -----------------------------------------------
    # Load through JDBC
    # -----------------------------------------------
    return (
        spark.read.format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", query)
        .option("user", username)
        .option("password", password)
        .option("driver", "org.postgresql.Driver")
        .load()
    )