import sqlglot

def validate_sql(sql_text: str) -> bool:
    try:
        sqlglot.parse(sql_text)
        return True
    except:
        return False
