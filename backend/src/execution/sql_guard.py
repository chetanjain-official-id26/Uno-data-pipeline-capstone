import re

from src.constants.constants import SQL_BLOCKED_KEYWORDS
class SQLGuard:

    BLOCKED_KEYWORDS = SQL_BLOCKED_KEYWORDS

       

    @classmethod
    def validate(cls, sql: str):

        if not sql:
            raise ValueError(
                "Transformation SQL cannot be empty"
            )

        sql = sql.strip()

        if not re.match(
            r"^(SELECT|WITH)\b",
            sql,
            re.IGNORECASE
        ):
            raise ValueError(
                "Only SELECT or WITH queries are allowed"
            )

        for keyword in cls.BLOCKED_KEYWORDS:

            if re.search(
                rf"\b{keyword}\b",
                sql,
                re.IGNORECASE
            ):
                raise ValueError(
                    f"Blocked SQL operation: {keyword}"
                )

        return True