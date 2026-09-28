
from pyspark.sql import DataFrame


def write_target(
    dataframe: DataFrame,
    target: dict,
) -> None:

    connection = target["connection"]

    table = target["table"]

    write_mode = target["write_mode"]

    connection_type = connection["type"]

    if connection_type == "postgresql":

        (
            dataframe.write
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
            .mode(
                write_mode.lower()
            )
            .save()
        )

        return

    raise ValueError(
        f"Unsupported target type: {connection_type}"
    )

