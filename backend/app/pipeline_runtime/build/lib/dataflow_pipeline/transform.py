from pyspark.sql import DataFrame, SparkSession


class TransformationExecutor:

    def execute(
        self,
        spark: SparkSession,
        source_df: DataFrame,
        transformations: list[dict],
    ) -> DataFrame:

        source_df.createOrReplaceTempView(
            "raw_data"
        )

        result = source_df

        for transformation in sorted(
            transformations,
            key=lambda item: item["step_order"],
        ):

            result = spark.sql(
                transformation["sql_query"]
            )

            result.createOrReplaceTempView(
                transformation["output_view"]
            )

        return result