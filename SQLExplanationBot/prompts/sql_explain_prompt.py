from langchain_core.prompts import PromptTemplate

sql_explain_prompt = PromptTemplate(
    template="""
You are an expert SQL tutor.

Explain the following SQL query step by step in simple and clear language.
Focus on:
- What each clause does
- How the final result is produced
- Do NOT return the explanation and example
- Return only crisp answer

SQL Query:
{sql_query}
""",
    input_variables=["sql_query"]
)
