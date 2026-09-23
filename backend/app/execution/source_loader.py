from pyspark.sql import DataFrame, SparkSession


def load_sample_from_cockroach(
    spark: SparkSession,
    connection: dict,
    table_name: str,
    limit: int = 100,
) -> DataFrame:
    """Load a limited sample from a CockroachDB table."""

    jdbc_url = (
        f"jdbc:postgresql://"
        f"{connection['host']}:"
        f"{connection['port']}/"
        f"{connection['database']}"
    )

    query = f"""
        (
            SELECT *
            FROM {table_name}
            LIMIT {limit}
        ) AS source_data
    """

    return (
        spark.read
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", query)
        .option("user", connection["username"])
        .option("password", connection["password"])
        .option("driver", "org.postgresql.Driver")
        .load()
    )