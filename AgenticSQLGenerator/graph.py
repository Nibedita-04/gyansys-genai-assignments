from langgraph.graph import StateGraph, END
from state import SQLAgentState
from tools import (
    detect_intent,
    nl_to_sql,
    fix_sql,
    format_answer,
    handle_unrelated
)

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
graph.add_node("nl_to_sql", nl_to_sql)
graph.add_node("fix_sql", fix_sql)
graph.add_node("format_answer", format_answer)
graph.add_node("handle_unrelated", handle_unrelated)

graph.set_entry_point("intent_detection")

# Route based on intent
graph.add_conditional_edges(
    "intent_detection",
    check_intent,
    {
        "nl_query": "nl_to_sql",
        "unrelated_query": "handle_unrelated"
    }
)

# NL -> SQL flow
graph.add_edge("nl_to_sql", "format_answer")  
graph.add_edge("handle_unrelated", END)

# Retry loop if error occurs (optional if execute_sql is added)
graph.add_conditional_edges(
    "format_answer",
    check_error,
    {
        "retry": "fix_sql",
        "success": END,
        "fail": END
    }
)

graph.add_edge("fix_sql", "format_answer")

app = graph.compile()