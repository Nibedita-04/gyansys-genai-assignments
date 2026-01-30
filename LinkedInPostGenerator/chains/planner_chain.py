from config.llm import get_llm
from prompts.planner_prompt import planner_prompt

planner_chain = planner_prompt | get_llm()