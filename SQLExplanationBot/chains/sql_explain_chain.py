from prompts.sql_explain_prompt import sql_explain_prompt

def sql_explain_chain(llm, sql_query):
    """
    Explains SQL in natural language.
    """

    messages = sql_explain_prompt.format_messages(
        sql_query=sql_query
    )

    response = llm.invoke(messages)

    return response.content
