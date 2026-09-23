from pyspark.sql import DataFrame

from app.execution.source_loader import load_sample_from_cockroach
from app.execution.spark_session import create_spark_session


class PreviewExecutor:
    """Executes pipeline transformations using local PySpark."""

    def preview(
        self,
        connection: dict,
        source_table: str,
        steps: list[dict],
        target_step_order: int,
    ) -> dict:

        spark = create_spark_session()

        try:
            # 1. Load source sample
            source_df = load_sample_from_cockroach(
                spark=spark,
                connection=connection,
                table_name=source_table,
                limit=100,
            )

            # 2. Create raw_data
            source_df.createOrReplaceTempView("raw_data")

            result: DataFrame | None = None

            # 3. Execute steps in order
            for step in steps:

                if step["step_order"] > target_step_order:
                    break

                result = spark.sql(
                    step["sql_query"]
                )

                result.createOrReplaceTempView(
                    step["output_view"]
                )

            if result is None:
                raise ValueError(
                    "No transformation step was executed."
                )

            # 4. Convert result to API response
            return self._to_response(result)

        finally:
            spark.stop()

    def _to_response(
        self,
        dataframe: DataFrame,
    ) -> dict:

        rows = dataframe.limit(100).collect()

        return {
            "columns": dataframe.columns,
            "rows": [
                row.asDict()
                for row in rows
            ],
        }