from langchain_core.output_parsers import StrOutputParser
from config import get_llm
from prompts.nl_to_sql_prompt import nl_to_sql_prompt

llm = get_llm()

nl_to_sql_chain = nl_to_sql_prompt | llm | StrOutputParser()

def generate_sql(question: str, schema: str) -> str:
    result = nl_to_sql_chain.invoke({"question": question, "schema": schema})
    return result.strip()
