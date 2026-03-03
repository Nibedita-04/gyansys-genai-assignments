from langgraph.graph import StateGraph, END
from state import SQLAgentState
from tools import (
    detect_intent,
    nl_to_sql,
    fix_sql,
    format_answer,
    handle_unrelated,
    evaluate_sql_with_retry,
    execute_sql_with_retry,
)
from nodes.table_selector import select_tables
from nodes.column_selector import select_columns

MAX_RETRIES = 2

# ----------------------------
# Helper functions
# ----------------------------

def check_intent(state):
    """Route based on detected intent"""
    return state["intent"]

def check_execute_sql_with_skip(state):
    if state.get("skip_fix"):
        return "success"  # Skip fix, go to evaluate or format
    return "retry" if state.get("error") else "success"

# ----------------------------
# Build Graph
# ----------------------------
graph = StateGraph(SQLAgentState)

# Add nodes
graph.add_node("intent_detection", detect_intent)
graph.add_node("table_selector", select_tables)
graph.add_node("column_selector", select_columns)
graph.add_node("nl_to_sql", nl_to_sql)
graph.add_node(
    "execute_sql", 
    lambda state: execute_sql_with_retry(state, MAX_RETRIES=MAX_RETRIES)
)
graph.add_node(
    "evaluate_sql", 
    lambda state: evaluate_sql_with_retry(state, MAX_RETRIES=MAX_RETRIES)
)
graph.add_node("fix_sql", fix_sql)
graph.add_node("format_answer", format_answer)
graph.add_node("handle_unrelated", handle_unrelated)

# Entry point
graph.set_entry_point("intent_detection")

# ----------------------------
# Intent routing
# ----------------------------
graph.add_conditional_edges(
    "intent_detection",
    check_intent,
    {
        "nl_query": "table_selector",
        "unrelated_query": "handle_unrelated"
    }
)

# ----------------------------
# Main NL → SQL Flow
# ----------------------------
graph.add_edge("table_selector", "column_selector")
graph.add_edge("column_selector", "nl_to_sql")

# Execute SQL
graph.add_edge("nl_to_sql", "execute_sql")

# If SQL failed → fix_sql, else → evaluate_sql
graph.add_conditional_edges(
    "execute_sql",
    check_execute_sql_with_skip,
    {
        "retry": "fix_sql",
        "success": "evaluate_sql"
    }
)

# Evaluate SQL correctness → if LLM says correct → format_answer else → fix_sql
graph.add_conditional_edges(
    "evaluate_sql",
    lambda state: "success" if state.get("skip_fix") else ("retry" if state.get("needs_fix") else "success"),
    {
        "retry": "fix_sql",
        "success": "format_answer"
    }
)

# Retry loop from fix_sql → nl_to_sql
graph.add_edge("fix_sql", "execute_sql")

# Final formatting and unrelated handler go straight to END
graph.add_edge("format_answer", END)
graph.add_edge("handle_unrelated", END)

# Compile final graph
app = graph.compile()