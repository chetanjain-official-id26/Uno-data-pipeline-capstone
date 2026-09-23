from pyspark.sql import DataFrame


class TargetWriter:

    def write(
        self,
        df: DataFrame,
        jdbc_url: str,
        username: str,
        password: str,
        target_table: str,
        write_mode: str,
    ) -> int:

        if write_mode not in {
            "APPEND",
            "OVERWRITE",
        }:
            raise ValueError(
                f"Unsupported write mode: {write_mode}"
            )

        (
            df.write
            .format("jdbc")
            .option("url", jdbc_url)
            .option("dbtable", target_table)
            .option("user", username)
            .option("password", password)
            .option(
                "driver",
                "org.postgresql.Driver",
            )
            .mode(
                write_mode.lower()
            )
            .save()
        )

        return df.count()