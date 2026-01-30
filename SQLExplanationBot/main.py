from chains.sql_explain_chain import explain_sql
from chains.nl_to_sql_chain import generate_sql
from utils.intent_detector import detect_intent


def process_user_input(user_input: str) -> str:
    cleaned_input = user_input.strip()

    if "Question:" in cleaned_input or "Schema:" in cleaned_input:
        question = cleaned_input.split("Schema:")[0].replace("Question:", "").strip()
        schema = cleaned_input.split("Schema:")[1].strip()
        return generate_sql(question, schema)

    intent = detect_intent(cleaned_input)

    if intent == "SQL_TO_NLP":
        return explain_sql(cleaned_input)

    return (
        "For SQL generation, please provide input in the format:\n\n"
        "Question:\n<your question>\n\nSchema:\n<database schema>"
    )


if __name__ == "__main__":
    print("=== SQL Assistant ===")
    print("Paste SQL OR provide Question + Schema\n")

    user_input = input("Input:\n")
    output = process_user_input(user_input)

    print("\n=== Output ===")
    print(output)
