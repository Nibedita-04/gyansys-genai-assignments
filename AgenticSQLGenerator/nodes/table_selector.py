from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from database import get_schema_metadata
from schema import TableSelectionOutput
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

# LLM selelcts the tables as per the given user question and available tables
def select_tables(state):
    user_query = state["user_input"]
    schema = get_schema_metadata()
    table_list = list(schema.keys())

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a database expert.
        Given a user question and available tables,
        select ONLY the relevant tables needed to answer the question.
        Match user terms with semantically similar table names.
        Plural and singular forms should be considered equivalent.
        If a location is mentioned, check for columns like city or location.
        Return only valid JSON.
        """),
        ("human", f"""
        <User Question>
        {user_query}
        </User Question>

        <Available Tables>
        {table_list}
        </Available Tables>
        """)
    ])

    structured_llm = llm.with_structured_output(TableSelectionOutput)
    response = structured_llm.invoke(prompt.format_messages())

    tables = response.model_dump().get("tables")

    # Defensive handling
    if not tables:
        tables = []

    state["selected_tables"] = tables
    return state