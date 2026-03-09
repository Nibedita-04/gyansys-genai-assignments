from typing import TypedDict, Any, Dict
from langgraph.graph import StateGraph, END

from graphs.resume_graph import build_resume_graph
from graphs.jd_graph import build_jd_graph


class MasterState(TypedDict, total=False):
    input_type: str
    file_path: str

    # JD outputs
    jd_path: str
    jd_hash: str
    parsed_text: str
    structured: Dict[str, Any]
    embedding: Any
    cached: bool
    results: Any
    reranked_results: Any


def build_master_graph():

    workflow = StateGraph(MasterState)

    resume_graph = build_resume_graph()
    jd_graph = build_jd_graph()

    # --- Adapter wrappers ---

    def run_resume(state: MasterState):
        sub_state = {
            "resume_path": state["file_path"]
        }

        result = resume_graph.invoke(sub_state)

        return {**state, **result}

    def run_jd(state: MasterState):
        sub_state = {
            "jd_path": state["file_path"]
        }

        result = jd_graph.invoke(sub_state)
        # print("SUBGRAPH RETURN:", result)
        # merge subgraph result into master state
        return {**state, **result}

    # Add nodes
    workflow.add_node("resume_flow", run_resume)
    workflow.add_node("jd_flow", run_jd)

    # Router
    def route(state: MasterState):
        if state["input_type"] == "resume":
            return "resume_flow"
        return "jd_flow"

    workflow.set_conditional_entry_point(route)

    workflow.add_edge("resume_flow", END)
    workflow.add_edge("jd_flow", END)

    return workflow.compile()