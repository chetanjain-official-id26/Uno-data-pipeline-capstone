
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def apply_transformations(
    dataframe: DataFrame,
    transformations: list[dict],
) -> DataFrame:

    ordered = sorted(
        transformations,
        key=lambda step: step.get(
            "order",
            0,
        ),
    )

    for step in ordered:

        step_type = step["type"]

        config = step.get(
            "config",
            {},
        )

        if step_type == "FILTER":

            dataframe = dataframe.filter(
                _build_filter(config)
            )

        elif step_type == "SELECT":

            columns = config["columns"]

            dataframe = dataframe.select(
                *columns
            )

        elif step_type == "RENAME":

            dataframe = dataframe.withColumnRenamed(
                config["source"],
                config["target"],
            )

        elif step_type == "DROP":

            dataframe = dataframe.drop(
                *config["columns"]
            )

        elif step_type == "CAST":

            dataframe = dataframe.withColumn(
                config["column"],
                F.col(
                    config["column"]
                ).cast(
                    config["data_type"]
                ),
            )

        else:

            raise ValueError(
                f"Unsupported transformation: {step_type}"
            )

    return dataframe


def _build_filter(
    config: dict,
):

    column = F.col(
        config["column"]
    )

    operator = config["operator"]

    value = config.get(
        "value"
    )

    if operator == "=":
        return column == value

    if operator == "!=":
        return column != value

    if operator == ">":
        return column > value

    if operator == ">=":
        return column >= value

    if operator == "<":
        return column < value

    if operator == "<=":
        return column <= value

    if operator == "IS_NULL":
        return column.isNull()

    if operator == "IS_NOT_NULL":
        return column.isNotNull()

    raise ValueError(
        f"Unsupported filter operator: {operator}"
    )

