def detect_intent(user_input: str) -> str:
    sql_keywords = [
        "select", "from", "where", "group by",
        "order by", "join", "having", "limit"
    ]

    lowered = user_input.lower()

    if any(keyword in lowered for keyword in sql_keywords):
        return "SQL_TO_NLP"

    return "NLP_TO_SQL"
