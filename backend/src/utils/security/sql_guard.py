import re

from src.constants import SQL_BLOCKED_KEYWORDS


class SQLGuard:
    """Validate transformation SQL before Spark execution."""

    BLOCKED_KEYWORDS = SQL_BLOCKED_KEYWORDS

    @classmethod
    def validate(
        cls,
        sql: str,
    ) -> bool:

        if not sql:
            raise ValueError(
                "Transformation SQL cannot be empty"
            )

        sql = sql.strip()

        if not sql:
            raise ValueError(
                "Transformation SQL cannot be empty"
            )

        # Only SELECT and WITH queries are allowed.
        if not re.match(
            r"^(SELECT|WITH)\b",
            sql,
            re.IGNORECASE,
        ):
            raise ValueError(
                "Only SELECT or WITH queries are allowed"
            )

        for keyword in cls.BLOCKED_KEYWORDS:

            if re.search(
                rf"\b{re.escape(keyword)}\b",
                sql,
                re.IGNORECASE,
            ):
                raise ValueError(
                    f"Blocked SQL operation: {keyword}"
                )

        return True