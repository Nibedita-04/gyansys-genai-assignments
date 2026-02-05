from datetime import datetime
from config.llm import get_llm
from langchain_core.prompts import PromptTemplate
from memory.embedding_model import get_embedding
from memory.user_manager import get_user_collection

MAX_MEMORY = 5


def init_user(user_id, user_name):
    # Ensures collection exists
    get_user_collection(user_id)


def add_summary(user_id, role, post_idea, generated_post):
    collection = get_user_collection(user_id)

    text = f"Role: {role} | Idea: {post_idea} | Post: {generated_post}"
    embedding = get_embedding(text)

    collection.add(
        documents=[text],
        embeddings=[embedding],
        metadatas=[{
            "role": role,
            "idea": post_idea,
            "timestamp": datetime.now().isoformat()
        }],
        ids=[str(hash(text))]
    )


def get_recent_memory(user_id):
    collection = get_user_collection(user_id)

    results = collection.get()

    if not results["documents"]:
        return []

    return results["documents"][-MAX_MEMORY:]


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



