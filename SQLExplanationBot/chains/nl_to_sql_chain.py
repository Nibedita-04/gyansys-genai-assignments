from prompts.nl_to_sql_prompt import nl_to_sql_prompt
from utils.sql_validator import validate_sql

MAX_RETRIES = 3

def nl_to_sql_chain(llm, user_query, schema=""):
    """
    Converts natural language to SQL.
    Returns ONLY SQL if valid.
    """

    for attempt in range(MAX_RETRIES):

        # Format the structured prompt
        messages = nl_to_sql_prompt.format_messages(
            user_query=user_query,
            schema=schema
        )

        # Call LLM
        response = llm.invoke(messages)
        sql_output = response.content.strip()

        # Validate SQL syntax
        if validate_sql(sql_output):
            return sql_output

    raise ValueError("LLM failed to generate valid SQL")
