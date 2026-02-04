from config.llm import get_llm
from langchain_core.prompts import PromptTemplate

llm = get_llm()

prompt = PromptTemplate(
    input_variables = ["post_idea"],
    template = """
    You are a reasoning assistant for LinkedIn content.

    Your task:
    1. Understand the user's intent.
    2. Detect typos.
    3. If a typo looks like a technical term, library, framework, or product name, correct it to the MOST LIKELY technical term.
    4. NEVER replace technical terms with generic words.
    5. Preserve names like: LangGraph, LangChain, RAG, FAISS, Groq, LLM, OpenAI, etc.
    6. Fix only real spelling mistakes.
    7. Output ONLY the corrected and intent-preserving idea.
    
    <user idea>
    {post_idea}
    </user idea>
    """
)

stepback_chain = prompt | llm