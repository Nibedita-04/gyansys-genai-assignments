from langchain_core.prompts import ChatPromptTemplate

nl_to_sql_prompt = ChatPromptTemplate.from_template("""
<input_variables>
<user_query>{user_query}</user_query>
<schema>{schema}</schema>
</input_variables>

<system_rules>
You are an expert SQL generator.
Return ONLY valid SQL.
Do NOT explain.
Do NOT hallucinate table or column names.
Follow SQL best practices.
</system_rules>

<task>
Convert the natural language query into SQL.
</task>
""")

