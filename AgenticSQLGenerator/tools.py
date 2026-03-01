from langchain_openai import AzureChatOpenAI
from database import get_schema_metadata, get_foreign_key_graph
import os
from dotenv import load_dotenv
import json
import sqlite3
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


# INTENT DETECTION - detects the intent of the query whether its a Nl query or unrelated query

def detect_intent(state):
    structured_llm = llm.with_structured_output(IntentOutput)

    result = structured_llm.invoke(
        f"""
        Classify the user query into:

        1. "nl_query" → Database question
        2. "unrelated_query" → Not related to DB

        Query:
        {state["user_input"]}
        """
    )

    state["intent"] = result.intent
    return state


# NL → SQL GENERATION - converts the Natural Language to SQL

def nl_to_sql(state):
    user_query = state["user_input"]
    selected_tables = state.get("selected_tables")
    selected_columns = state.get("selected_columns")

    if not selected_tables or not selected_columns:
        state["error"] = "Missing table or column selection"
        return state

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
                    join_clauses.append({
                        "from": t1,
                        "to": t2,
                        "condition": condition
                    })

    prompt = f"""
    You are a deterministic SQLite query planner.

    <DATABASE SCHEMA>
    {schema_str}
    </DATABASE SCHEMA>

    <SELECTED TABLES>
    {selected_tables}
    </SELECTED TABLES>

    <SELECTED COLUMNS>
    {selected_columns}
    </SELECTED COLUMNS>

    <JOIN PATHS>
    {join_paths}
    </JOIN PATHS>

    <JOIN CONDITIONS>
    {join_clauses}
    </JOIN CONDITIONS>

    <USER QUESTION>
    {user_query}
    </USER QUESTION>

    Output ONLY valid SQLite SQL.
    """

    structured_llm = llm.with_structured_output(
        SQLGenerationOutput,
        method="function_calling"
    )

    result = structured_llm.invoke(prompt)

    print("GENERATED SQL:", result.sql)

    state["generated_sql"] = result.sql.strip()
    state["error"] = None

    return state



# EXECUTE SQL - executes the genrated SQL query and returns the output if the details are present in the db

def execute_sql(state):
    try:
        conn = sqlite3.connect("database/enterprise.db")
        cursor = conn.cursor()

        print("EXECUTING SQL:", state["generated_sql"])

        cursor.execute(state["generated_sql"])
        rows = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        result = [dict(zip(columns, row)) for row in rows]

        print("SQL RESULT:", result)

        state["sql_result"] = result
        state["error"] = None

        conn.close()

    except Exception as e:
        print("SQL ERROR:", str(e))
        state["error"] = str(e)
        state["sql_result"] = None

    return state


# FIX SQL - If the SQL query failed then retry

def fix_sql(state):
    structured_llm = llm.with_structured_output(SQLFixOutput)

    result = structured_llm.invoke(
        f"""
        The SQL query failed.

        <SQL>
        {state['generated_sql']}
        </SQL>

        <Error>
        {state.get('error')}
        </Error>

        Fix it.
        """
    )

    state["generated_sql"] = result.corrected_sql.strip()
    state["retry_count"] += 1
    return state


# FORMAT FINAL ANSWER - generates a clean answer and the result of the SQL query

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

        Generate a clear business answer.
        """
    )

    state["final_answer"] = result.answer
    return state


# UNRELATED HANDLER - handles the questions which are out of the database

def handle_unrelated(state):
    state["final_answer"] = (
        "This question is not related to the database schema. "
        "Please ask a database-related question."
    )
    return state