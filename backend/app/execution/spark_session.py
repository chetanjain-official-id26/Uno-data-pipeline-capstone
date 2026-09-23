from pyspark.sql import SparkSession


def create_spark_session() -> SparkSession:
    """Create a local Spark session for preview execution."""

    return (
        SparkSession.builder
        .appName("DataFlowHubPreview")
        .master("local[*]")
        .getOrCreate()
    )