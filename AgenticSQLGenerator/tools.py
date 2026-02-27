from langchain_openai import AzureChatOpenAI
from database import get_schema_metadata, get_foreign_key_graph
import os
from dotenv import load_dotenv
import json
from schema import IntentOutput, SQLGenerationOutput, SQLFixOutput, FinalAnswerOutput
from join_planner import find_join_path

load_dotenv()

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("OPENAI_API_ENDPOINT"),
    azure_deployment=os.getenv("DEPLOYMENT_NAME"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)

SCHEMA = """
Tables:
customers(id, name, age, city)
orders(id, customer_id, amount, date)
"""

def detect_intent(state):
    structured_llm = llm.with_structured_output(IntentOutput)

    result = structured_llm.invoke(
        f"""
        You are classifying user intent for a database agent.

        Classify into one of:

        1. "nl_query" → Natural language question about the database.
        2. "unrelated_query" → Question not related to the database.

        <Database Schema>
        {SCHEMA}
        </Database Schema>
        
        <User Query>
        {state["user_input"]}
        </User Query>
        """
    )

    state["intent"] = result.intent
    return state

def nl_to_sql(state):
    user_query = state["user_input"]
    selected_tables = state["selected_tables"]
    selected_columns = state["selected_columns"]

    schema = get_schema_metadata()
    schema_str = json.dumps(schema, indent=2)

    adj_graph, join_conditions = get_foreign_key_graph()

    join_paths = []
    join_clauses = []

    if len(selected_tables) > 1:
        for i in range(len(selected_tables) - 1):
            start = selected_tables[i]
            end = selected_tables[i + 1]
            path = find_join_path(adj_graph, start, end)
            if not path:
                raise Exception(f"No join path found between {start} and {end}")
            join_paths.append(path)
            for j in range(len(path) - 1):
                t1, t2 = path[j], path[j + 1]
                condition = join_conditions.get((t1, t2))
                if condition:
                    join_clauses.append({"from": t1, "to": t2, "condition": condition})

    tables_str = ", ".join(selected_tables)
    columns_str = ", ".join(selected_columns)

    prompt = f"""
            <system_role>
            You are a deterministic SQLite query planner.
            You must strictly follow selected tables, columns, join paths, and ON conditions.
            Output ONLY valid SQLite SQL.
            </system_role>

            <schema>
            {schema_str}
            </schema>

            <tables>
            {tables_str}
            </tables>

            <columns>
            {columns_str}
            </columns>

            <join_paths>
            {json.dumps(join_paths, indent=2)}
            </join_paths>

            <join_conditions>
            {json.dumps(join_clauses, indent=2)}
            </join_conditions>

            <user_question>
            {user_query}
            </user_question>
            """

    structured_llm = llm.with_structured_output(SQLGenerationOutput, method="function_calling")
    result = structured_llm.invoke(prompt)
    state["generated_sql"] = result.sql.strip()
    return state

def fix_sql(state):
    structured_llm = llm.with_structured_output(SQLFixOutput)
    result = structured_llm.invoke(
        f"""
        The following SQL query failed:

        SQL:
        {state['generated_sql']}

        Error:
        {state.get('error')}

        Database Schema:
        {SCHEMA}

        Fix the SQL query.
        """
    )
    state["generated_sql"] = result.corrected_sql.strip()
    state["retry_count"] += 1
    return state

def format_answer(state):
    structured_llm = llm.with_structured_output(FinalAnswerOutput)
    result = structured_llm.invoke(
        f"""
        <User Question>
        {state['user_input']}
        </User Question>

        <SQL Result>
        {state.get('sql_result')}
        </SQL Result>

        Generate a clear answer.
        """
    )
    state["final_answer"] = result.answer
    return state

def handle_unrelated(state):
    state["final_answer"] = (
        "This question is not related to the database schema."
        "Please ask a database-related question."
    )
    return state