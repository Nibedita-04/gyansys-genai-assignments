from typing import TypedDict, Optional, List, Union

class SQLAgentState(TypedDict, total=False):
    user_input: str
    intent: Optional[str]
    selected_tables: Optional[List[str]]
    selected_columns: Optional[List[str]]
    generated_sql: Optional[str]
    sql_result: Optional[Union[List[dict], None]]
    explanation: Optional[str]
    error: Optional[str]
    retry_count: int         # count of how many times fix_sql was applied
    final_answer: Optional[str]
    needs_fix: bool
    retries: int             # count of total retries including execute_sql and evaluate_sql
    skip_fix: bool           # flag to skip fix when MAX_RETRIES exceeded