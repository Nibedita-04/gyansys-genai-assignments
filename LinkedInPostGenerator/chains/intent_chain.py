from config.llm import get_llm
from prompts.intent_prompt import intent_prompt

intent_chain = intent_prompt | get_llm()

