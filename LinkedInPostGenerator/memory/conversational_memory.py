import json
from pathlib import Path
from datetime import datetime
from config.llm import get_llm
from langchain_core.prompts import PromptTemplate

MEMORY_FILE = Path("memory_history.json")
MAX_MEMORY = 5

def load_memory():
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r", encoding = "utf-8") as f:
            return json.load(f)
    return {"users": {}}
    
def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent = 2, ensure_ascii=False)

def init_user(user_id, user_name):
    data = load_memory()

    if user_id not in data["users"]:
        data["users"][user_id] = {
            "name": user_name,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "interactions": []
        }

        save_memory(data)


def add_summary(user_id, role, post_idea, generated_post):
    
    data = load_memory()

    if user_id not in data["users"]:
        raise ValueError("User not initialized. Call init_user(user_id, name) first.")
    
    interaction = {
        "role": role,
        "post_idea": post_idea,
        "generated_post": generated_post,
        "timestamp": datetime.now().isoformat()
    }

    data["users"][user_id]["interactions"].append(interaction)

    data["users"][user_id]["interactions"] = data["users"][user_id]["interactions"][-MAX_MEMORY:]

    save_memory(data)

def get_recent_memory(user_id):
    data = load_memory()

    if user_id not in data["users"]:
        return []
    
    interactions = data["users"][user_id]["interactions"]

    return [
        f"Role: {x['role']} | Idea: {x['post_idea']} | Post: {x['generated_post']}" for x in interactions[-MAX_MEMORY:]

    ]

def get_user_style(user_id):
    recent_memory = get_recent_memory(user_id)

    if not recent_memory:
        return "Professional, concise, and insightful"
    
    llm = get_llm()

    prompt = PromptTemplate(
        input_variables=["recent_memory"],
        template="""
        Analyze the writing style from these past LinkedIn post summaries:

        <recent_memory>
        {recent_memory}
        </recent_memory>
        
        Return a short style description in 5–10 words.
        Examples: "Reflective, technical, concise"
        Return ONLY the style text.
        """
        
        )

    chain = prompt | llm
    
    response = chain.invoke({
        "recent_memory": "\n".join(recent_memory)
    })

    return response.content.strip()



