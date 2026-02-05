from chains.role_chain import role_chain
from chains.intent_chain import intent_chain
from chains.planner_chain import planner_chain
from chains.generator_chain import generator_chain
from chains.stepback_chain import stepback_chain
from memory.conversational_memory import get_user_style, add_summary, get_recent_memory
from memory.conversational_memory import init_user
from memory.memory_retriever import retrieve_memory

MIN_WORD_LIMIT = 80

session_mode = input("Choose session mode (linked / standalone): ").strip().lower()


def run_pipeline(user_id, user_role, post_idea, word_limit, emoji_count, hashtag_count):
    
    if word_limit < MIN_WORD_LIMIT:
        return f"Word limit too low. Please enter at least {MIN_WORD_LIMIT} words."

    role_info = role_chain.invoke({"user_role": user_role}).content
    
    refined_idea = stepback_chain.invoke({
        "post_idea": post_idea
    }).content

    intent_info = intent_chain.invoke({
        "role": role_info,
        "post_idea": refined_idea
    }).content

    plan = planner_chain.invoke({
        "role_info": role_info,
        "intent_info": intent_info,
        "post_idea": refined_idea
    }).content

    # recent_memory = get_recent_memory(user_id)  

    recent_memory = retrieve_memory(user_id, post_idea, k=5, mode=session_mode)
    print("---- RETRIEVED MEMORY ----")
    print(recent_memory)
    print("--------------------------")


    user_style = get_user_style(user_id)

    final_post = generator_chain.invoke({
        "role_info": role_info,
        "post_plan": plan,
        "post_idea": refined_idea,
        "user_style": user_style,
        "recent_memory": "\n".join(recent_memory) if recent_memory else "None",
        "word_limit": word_limit,
        "emoji_count": emoji_count,
        "hashtag_count": hashtag_count
    }).content

    
    add_summary(user_id, user_role, post_idea + " -> " + refined_idea, final_post)

    return final_post


if __name__ == "__main__":
    user_id = input("Enter your User ID: ")
    user_name = input("Enter your Name: ")

    init_user(user_id, user_name)

    user_role = input("Describe your role: ")
    post_idea = input("Describe your post idea: ")
    word_limit_input = input("Enter word limit for post (min 80 recommended): ")
    emoji_count = int(input("Enter emoji count: "))
    hashtag_count = int(input("Enter hashtag count: "))

    try:
        word_limit = int(word_limit_input)
    except ValueError:
        print("\nWord limit must be a number.")
        exit()

    post = run_pipeline(user_id, user_role, post_idea, word_limit, emoji_count, hashtag_count)

    print("\n--- GENERATED LINKEDIN POST ---\n")
    print(post)

