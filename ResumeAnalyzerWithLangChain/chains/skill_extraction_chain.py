import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableSequence

from prompts.skill_extraction_prompt import get_skill_extraction_prompt
load_dotenv()

def get_skill_extraction_chain():
    llm = ChatGroq(
        api_key = os.getenv("GROQ_API_KEY"),
        model = "llama-3.1-8b-instant",
        temperature = 0
    )

    prompt, parser = get_skill_extraction_prompt()

    chain = prompt | llm | parser

    return chain