from graph import app
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def run_agent():
    print("Enterprise SQL Agent")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Enter your query: ")
        if user_input.lower() == "exit":
            break

        state = {
            "user_input": user_input,
            "intent": None,
            "selected_tables": None,
            "selected_columns": None,
            "generated_sql": None,
            "sql_result": None,
            "explanation": None,
            "error": None,
            "retry_count": 0,
            "final_answer": None
        }

        result = app.invoke(state)
        print("\nFinal Answer:")
        print(result.get("final_answer"))
        print("-" * 50)


if __name__ == "__main__":
    # Run once if DB not created
    # initialize_database()

    run_agent()