from langchain_core.prompts import ChatPromptTemplate

planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert LinkedIn content planner."
        ),
        (
            "human",
            """
            You are given:
- User role information
- Post intent
- Post idea

Role info:
{role_info}

Intent info:
{intent_info}

Post idea:
{post_idea}

Based on this, create a clear LinkedIn post plan.

Decide:
1. Appropriate tone
2. Target audience
3. Logical post structure (ordered list)
4. Suggested call-to-action (CTA)

Respond in JSON with keys:
- tone
- audience
- post_structure
- cta
            """
        )
    ]
)