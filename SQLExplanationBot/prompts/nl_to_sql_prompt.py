from langchain_core.prompts import PromptTemplate

nl_to_sql_prompt = PromptTemplate(
    template="""
You are an expert SQL generator. Use Chain-of-Thought reasoning internally
to derive the correct SQL query, but DO NOT include any reasoning in the output.
Only return the final SQL query.

Rules:
1. Analyze the question carefully.
2. If the question compares groups (e.g., departments, categories),
   use aggregation (AVG, SUM, COUNT, MAX) with GROUP BY.
3. Words like "best", "top", "highest" imply group-level aggregation unless stated otherwise.
4. Use only tables and columns provided in the schema.
5. Output ONLY the final SQL query — no explanations, no comments.
6. Words like "best", "top", or "highest" imply group-level aggregation with AVG, SUM, or MAX.

Question:
{question}

Schema:
{schema}

SQL Query:
""",
    input_variables=["question", "schema"]
)
