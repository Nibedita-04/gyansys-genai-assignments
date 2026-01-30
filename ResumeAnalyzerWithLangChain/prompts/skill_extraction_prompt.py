from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from schemas.skill_schema import SkillExtraction

def get_skill_extraction_prompt():
    parser = PydanticOutputParser(pydantic_object = SkillExtraction)

    prompt = PromptTemplate(
        template = """
        You are an expert resume parser.

        Extract skills from the resume text below.

        RULES:
        1. Extract ONLY skills explicitly mentioned in the resume.
        2. Do NOT infer or guess skills.
        3. Categorize skills correctly.
        4. If a category has no skills, return an empty list.
        5. Do NOT add extra fields.
        6. Output MUST be valid JSON.
        7. Extract the candidate's full name. If missing, return null.

        {format_instructions}

        RESUME TEXT:
        {resume_text}
        """,
        input_variables = ["resume_text"],
        partial_variables = {
            "format_instructions": parser.get_format_instructions()
        },
    )

    return prompt, parser