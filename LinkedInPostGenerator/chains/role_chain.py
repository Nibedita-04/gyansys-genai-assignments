from config.llm import get_llm
from prompts.role_prompt import role_prompt

role_chain = role_prompt | get_llm()
