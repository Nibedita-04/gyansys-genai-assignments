from langchain_core.prompts import ChatPromptTemplate

intent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You analyze the intent behind LinkedIn post ideas."
        ),
        (
            "human",
            """

User Role:
{role}
            
Post idea:
{post_idea}

Identify the primary intent of this post.

Choose the closest matching intent from:
- Achievement
- Learning Update
- Project Launch
- Job Search
- Hiring
- Personal Branding

Also give a short one-line reasoning.

Respond in JSON with keys:
- intent
- reasoning
            """
        )
    ]
)