from pyspark.sql import DataFrame, SparkSession


class SourceLoader:

    def load(
        self,
        spark: SparkSession,
        jdbc_url: str,
        username: str,
        password: str,
        source_table: str,
    ) -> DataFrame:

        return (
            spark.read
            .format("jdbc")
            .option("url", jdbc_url)
            .option("dbtable", source_table)
            .option("user", username)
            .option("password", password)
            .option(
                "driver",
                "org.postgresql.Driver",
            )
            .load()
        )