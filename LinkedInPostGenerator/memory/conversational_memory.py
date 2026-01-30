import json
from pathlib import Path
from config.llm import get_llm
from langchain_core.prompts import PromptTemplate

MEMORY_FILE = Path("memory_history.json")

def add_summary(post_summary):
    
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
    else:
        memory = []

    memory.append(post_summary)

    memory = memory[-5:]

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def get_recent_memory():
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
        return memory[-5:]
    return []

def get_user_style():
    recent_memory = get_recent_memory()

    if not recent_memory:
        return "Professional, concise, and insightful"
    
    llm = get_llm()

    prompt = PromptTemplate(
        template="""
        Analyze the writing style from these past LinkedIn post summaries:

        {recent_memory}

        Return a short style description in 5–10 words.
        Examples: "Reflective, technical, concise"
        Return ONLY the style text.
        """,
        input_variables=["recent_memory"]
        )

    chain = prompt | llm
    
    response = chain.invoke({
        "recent_memory": "\n".join(recent_memory)
    })

    return response.content.strip()



