from langchain_core.output_parsers import StrOutputParser
from config import get_llm
from prompts.sql_explain_prompt import sql_explain_prompt

llm = get_llm()

sql_explain_chain = sql_explain_prompt | llm | StrOutputParser()

def explain_sql(sql_query: str) -> str:
    return sql_explain_chain.invoke({"sql_query": sql_query})
