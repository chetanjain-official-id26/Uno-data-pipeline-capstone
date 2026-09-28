
from pyspark.sql import DataFrame, SparkSession


def load_source(
    spark: SparkSession,
    source: dict,
) -> DataFrame:

    connection = source["connection"]

    table = source["table"]

    connection_type = connection["type"]

    if connection_type == "postgresql":

        return (
            spark.read
            .format("jdbc")
            .option(
                "url",
                connection["jdbc_url"],
            )
            .option(
                "dbtable",
                table,
            )
            .option(
                "user",
                connection["username"],
            )
            .option(
                "password",
                connection["password"],
            )
            .option(
                "driver",
                "org.postgresql.Driver",
            )
            .load()
        )

    raise ValueError(
        f"Unsupported source type: {connection_type}"
    )

