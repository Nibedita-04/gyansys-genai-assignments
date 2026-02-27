from langchain_core.prompts import ChatPromptTemplate

sql_explain_prompt = ChatPromptTemplate.from_template("""
<input_variables>
<sql_query>{sql_query}</sql_query>
</input_variables>

<system_rules>
You are an expert SQL teacher.
Explain step-by-step in simple language.
Explain the SQL query in natural language step by step and then finally give the complete meaning of the SQL query.
Do not rewrite SQL.
Do not give the response in markdown.
</system_rules>

<task>
Explain the SQL query clearly.
</task>
""")
