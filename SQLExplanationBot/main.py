from utils.intent_detector import is_complex_sql
from chains.nl_to_sql_chain import nl_to_sql_chain
from chains.sql_explain_chain import sql_explain_chain
from config import get_llm

llm = get_llm()

user_input = input("Enter your query: ")

if is_complex_sql(user_input):
    print("ROUTE: SQL → NL (Explain Mode)")
    output = sql_explain_chain(llm, user_input)

else:
    print("ROUTE: NL → SQL (Generate Mode)")
    output = nl_to_sql_chain(llm, user_input)

print("\nOUTPUT:\n", output)

