import re


class TableValidationError(ValueError):
    pass


TABLE_PATTERN = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?$"
)


def validate_table_name(table_name: str) -> str:

    table_name = table_name.strip()

    if not TABLE_PATTERN.fullmatch(table_name):
        raise TableValidationError(
            "Invalid table name"
        )

    return table_name