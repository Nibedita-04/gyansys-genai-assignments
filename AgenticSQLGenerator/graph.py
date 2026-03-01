from langgraph.graph import StateGraph, END
from state import SQLAgentState
from tools import (
    detect_intent,
    nl_to_sql,
    execute_sql, 
    fix_sql,
    format_answer,
    handle_unrelated
)
from nodes.table_selector import select_tables
from nodes.column_selector import select_columns

MAX_RETRIES = 2


def check_intent(state):
    return state["intent"]


def check_error(state):
    if state.get("error") and state["retry_count"] < MAX_RETRIES:
        return "retry"
    elif state.get("error"):
        return "fail"
    else:
        return "success"


graph = StateGraph(SQLAgentState)

graph.add_node("intent_detection", detect_intent)
graph.add_node("table_selector", select_tables)
graph.add_node("column_selector", select_columns)
graph.add_node("nl_to_sql", nl_to_sql)
graph.add_node("execute_sql", execute_sql)  
graph.add_node("fix_sql", fix_sql)
graph.add_node("format_answer", format_answer)
graph.add_node("handle_unrelated", handle_unrelated)

graph.set_entry_point("intent_detection")

# Intent Routing
graph.add_conditional_edges(
    "intent_detection",
    check_intent,
    {
        "nl_query": "table_selector",
        "unrelated_query": "handle_unrelated"
    }
)

# Main Flow
graph.add_edge("table_selector", "column_selector")
graph.add_edge("column_selector", "nl_to_sql")
graph.add_edge("nl_to_sql", "execute_sql") 
graph.add_edge("execute_sql", "format_answer")
graph.add_edge("handle_unrelated", END)

# Retry Loop
graph.add_conditional_edges(
    "format_answer",
    check_error,
    {
        "retry": "fix_sql",
        "success": END,
        "fail": END
    }
)

graph.add_edge("fix_sql", "execute_sql")

app = graph.compile()