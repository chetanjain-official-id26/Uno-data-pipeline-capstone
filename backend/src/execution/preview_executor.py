from typing import Any

from pyspark.sql import DataFrame

from src.execution.source_loader import load_sample_from_cockroach
from src.execution.spark_session import create_spark_session
from src.execution.sql_guard import SQLGuard


class PreviewExecutor:
    """Executes transformation SQL using local PySpark.

    Data is loaded from CockroachDB at runtime.
    Nothing needs to be permanently stored locally.
    """

    def preview(
        self,
        connection: dict[str, Any],
        source_table: str,
        steps: list[dict[str, Any]],
        preview_limit: int = 100,
    ) -> dict[str, Any]:
        if not source_table:
            raise ValueError("Source table cannot be empty")

        spark = create_spark_session()

        try:
            # ------------------------------------------------
            # 1. Load source data from CockroachDB
            # ------------------------------------------------
            source_df = load_sample_from_cockroach(
                spark=spark,
                connection=connection,
                table_name=source_table,
                limit=preview_limit,
            )

            # ------------------------------------------------
            # 2. Register source as raw_data
            # ------------------------------------------------
            source_df.createOrReplaceTempView("raw_data")

            # ------------------------------------------------
            # 3. If there are no transformations, return source preview.
            # ------------------------------------------------
            if not steps:
                rows = source_df.limit(preview_limit).collect()
                return {
                    "columns": source_df.columns,
                    "rows": [row.asDict() for row in rows],
                    "row_count": len(rows),
                }

            # ------------------------------------------------
            # 4. Execute transformations in order
            # ------------------------------------------------
            result: DataFrame = source_df
            ordered_steps = sorted(
                steps,
                key=lambda step: step["step_order"],
            )

            for step in ordered_steps:
                step_order = step["step_order"]
                sql_query = step.get("sql_query")
                input_view = step.get("input_view", "raw_data")
                output_view = step.get("output_view")

                if not sql_query:
                    raise ValueError(
                        f"SQL query is missing for step {step_order}"
                    )

                if not output_view:
                    output_view = f"step_{step_order}_out"

                # --------------------------------------------
                # Validate SQL
                # --------------------------------------------
                SQLGuard.validate(sql_query)

                # --------------------------------------------
                # Make sure the expected input view exists.
                #
                # For step 1: raw_data
                # For step 2: step_1_out
                # --------------------------------------------
                if not self._view_exists(spark, input_view):
                    raise ValueError(
                        f"Input view '{input_view}' does not exist for step {step_order}"
                    )

                # --------------------------------------------
                # Execute SQL
                # --------------------------------------------
                result = spark.sql(sql_query)

                # --------------------------------------------
                # Register output
                # --------------------------------------------
                result.createOrReplaceTempView(output_view)

            # ------------------------------------------------
            # 5. Convert final DataFrame to JSON
            # ------------------------------------------------
            rows = result.limit(preview_limit).collect()

            return {
                "columns": result.columns,
                "rows": [row.asDict() for row in rows],
                "row_count": len(rows),
            }

        finally:
            spark.stop()

    @staticmethod
    def _view_exists(
        spark,
        view_name: str,
    ) -> bool:
        return bool(spark.catalog.tableExists(view_name))