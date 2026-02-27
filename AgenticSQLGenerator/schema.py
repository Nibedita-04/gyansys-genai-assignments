from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict



# Intent Classification Output
class IntentOutput(BaseModel):
    intent: Literal["nl_query", "sql_query", "unrelated_query"] = Field(
        description="Intent of the user query"
    )



# NL → SQL Output
class SQLGenerationOutput(BaseModel):
    sql: str = Field(
        description="Valid SQLite SQL query generated from the user question"
    )



# SQL Fix Output
class SQLFixOutput(BaseModel):
    corrected_sql: str = Field(
        description="Corrected SQLite SQL query"
    )

# Final Answer Output
class FinalAnswerOutput(BaseModel):
    answer: str = Field(
        description="Clear natural language answer for the user"
    )

# schema for table selector output
class TableSelectionOutput(BaseModel):
    tables: List[str]

# schema for column selector output
class ColumnSelectionOutput(BaseModel):
    columns: List[str]