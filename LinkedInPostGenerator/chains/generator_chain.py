from config.llm import get_llm
from prompts.generator_prompt import generator_prompt

generator_chain = generator_prompt | get_llm()