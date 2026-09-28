from pyspark.sql import SparkSession

POSTGRES_JDBC_PACKAGE = "org.postgresql:postgresql:42.7.7"


def create_spark_session() -> SparkSession:
    """Create a local Spark session configured for PostgreSQL/CockroachDB JDBC."""
    return (
        SparkSession.builder.appName("DataFlowHubPreview")
        .master("local[*]")
        .config("spark.jars.packages", POSTGRES_JDBC_PACKAGE)
        .getOrCreate()
    )