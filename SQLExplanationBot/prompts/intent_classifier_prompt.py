from langchain_core.prompts import ChatPromptTemplate

intent_classifier_prompt = ChatPromptTemplate.from_template("""
<input_variables>
<user_input>{user_input}</user_input>
</input_variables>

<system_rules>
You are a strict classifier.
Decide if the input is SQL or Natural Language.
Return ONLY one label:

SQL_QUERY
NATURAL_LANGUAGE

No explanation.
</system_rules>

<task>
Classify the input.
</task>
""")
