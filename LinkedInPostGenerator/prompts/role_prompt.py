from langchain_core.prompts import ChatPromptTemplate

role_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
         "You are an expert LinkedIn content strategist."),
        ("human",
            """
            Identify the user's professional role from the input.

            Input:
            {user_role}

            Return a short normalized role name.
            """
        )
    ]
)