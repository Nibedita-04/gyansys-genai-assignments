from config.llm import get_llm
from langchain_core.prompts import PromptTemplate

llm = get_llm()

prompt = PromptTemplate(
    input_variables = ["post_idea"],
    template = """
    <user idea>
    {post_idea}
    </user idea>

    You are a reasoning assistant for LinkedIn content.

    Your task:
    1. Understand the user's intent.
    2. Detect typos.
    3. If a typo looks like a technical term, library, framework, or product name, correct it to the MOST LIKELY technical term.
    4. NEVER replace technical terms with generic words.
    5. Fix only real spelling mistakes.
    6. Output ONLY the corrected and intent-preserving idea.
    
    
    """
)

stepback_chain = prompt | llm