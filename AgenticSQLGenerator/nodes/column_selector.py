from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from database import get_schema_metadata
from schema import ColumnSelectionOutput
import json
import os
from dotenv import load_dotenv

load_dotenv()

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("OPENAI_API_ENDPOINT"),
    azure_deployment=os.getenv("DEPLOYMENT_NAME"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)

def select_columns(state):
    user_query = state["user_input"]
    selected_tables = state["selected_tables"]
    full_schema = get_schema_metadata()
    pruned_schema = {table: full_schema[table] for table in selected_tables}
    schema_str = json.dumps(pruned_schema, indent=2)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a database expert.
        Given a user question and table schemas,
        select ONLY the necessary columns needed to answer the question.
        Return only valid JSON.
        """),
        ("human", """
        <User Question>
        {user_query}
        </User Question>

        <Available Tables and Columns>
        {schema}
        </Available Tables and Columns>
        """)
    ])

    structured_llm = llm.with_structured_output(ColumnSelectionOutput, method="function_calling")
    response = structured_llm.invoke(
        prompt.format_messages(user_query=user_query, schema=schema_str)
    )

    state["selected_columns"] = response.columns
    return state