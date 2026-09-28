from pyspark.sql import DataFrame, SparkSession

from src.engine.table_validator import validate_table_name


class TargetWriter:

    def write(
        self,
        df: DataFrame,
        spark: SparkSession,
        jdbc_url: str,
        username: str,
        password: str,
        target_table: str,
        write_mode: str,
    ) -> int:

        target_table = validate_table_name(
            target_table
        )

        if write_mode not in {
            "APPEND",
            "OVERWRITE",
        }:
            raise ValueError(
                "Unsupported target write mode"
            )

        row_count = df.count()

        (
            df.write
            .format("jdbc")
            .option(
                "url",
                jdbc_url,
            )
            .option(
                "dbtable",
                target_table,
            )
            .option(
                "user",
                username,
            )
            .option(
                "password",
                password,
            )
            .option(
                "driver",
                "org.postgresql.Driver",
            )
            .mode(
                write_mode.lower()
            )
            .save()
        )

        return row_count