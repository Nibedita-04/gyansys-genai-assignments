from typing import TypedDict, Optional, List

class SQLAgentState(TypedDict):
    user_input: str
    intent: Optional[str]
    selected_tables: Optional[List[str]]
    selected_columns: Optional[List[str]]
    generated_sql: Optional[str]
    sql_result: Optional[str]
    explanation: Optional[str]
    error: Optional[str]
    retry_count: int
    final_answer: Optional[str]