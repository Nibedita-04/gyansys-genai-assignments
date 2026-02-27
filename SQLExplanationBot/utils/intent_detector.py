import sqlglot
import re

SQL_START_KEYWORDS = r"^\s*(WITH|SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)"

def is_complex_sql(text: str) -> bool:
    """
    Detect complex SQL including CTEs, joins, subqueries, enterprise SQL.
    """

    if not text or len(text.strip()) < 5:
        return False

    cleaned = text.strip()

    # Fast keyword confidence check
    if re.match(SQL_START_KEYWORDS, cleaned.upper()):
        return True

    # 2 SQLGlot multi-statement parser
    try:
        parsed = sqlglot.parse(cleaned)
        if parsed and len(parsed) > 0:
            return True
    except:
        pass

    return False


