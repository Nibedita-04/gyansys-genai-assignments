# src/retrieval/chapter_predictor.py
from langchain_openai import AzureChatOpenAI
from src.config import settings
import re
import json
from collections import Counter
from src.ingestion.vectordb import get_vectorstore
from langchain_core.prompts import PromptTemplate
# from src.schema.hsn_schema import HSNResponse

def get_llm():
    return AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_KEY,
        azure_deployment=settings.AZURE_CHAT_DEPLOYMENT,
        openai_api_version=settings.AZURE_API_VERSION,
        temperature=0
    )

# LLM call for CAS number lookup (if needed in future)
def lookup_cas_chemical(cas_number: str) -> str:
    """
    Lookup chemical name for a given CAS number using AzureChatOpenAI.
    Returns the chemical name as a string.
    """
    if not cas_number:
        return ""

    # Build prompt template
    prompt_template = """
    You are a chemical expert.
    Given the CAS number '{cas_number}', provide the standard chemical name.
    Only return the chemical name, properties, functions and industrial usage no explanations.
    """

    # Build chat prompt
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template("You are a helpful assistant that returns only chemical names."),
        HumanMessagePromptTemplate.from_template(prompt_template)
    ])

    # Format prompt and convert to messages
    formatted_prompt = chat_prompt.format_prompt(cas_number=cas_number)
    messages = formatted_prompt.to_messages()  # list of BaseMessage objects

    # Invoke LLM using the same pattern as predict_final_hsn
    llm = get_llm()
    response = llm.invoke(messages)
    chemical_name = response.content.strip()
    return chemical_name



# taking user input from excel sheet and generating a query out of it.
def generate_query(
    material_description: str,
    material_name: str,
    material_category: str,
    material_sub_category: str,
    raw_material_use_class: str,
    cas_number: str = None,
    country_of_origin: str = None
) -> str:

    # First, get chemical name from CAS number if provided
    cas_chemical_name = lookup_cas_chemical(cas_number) if cas_number else ""

    # Helper to clean text
    def clean_text(text: str) -> str:
        if not text:
            return ""
        return text.strip().replace("\n", " ").replace("\r", " ").lower()

    # Clean all inputs
    material_description = clean_text(material_description)
    material_name = clean_text(material_name)
    material_category = clean_text(material_category)
    material_sub_category = clean_text(material_sub_category)
    raw_material_use_class = clean_text(raw_material_use_class)
    country_of_origin = clean_text(country_of_origin) if country_of_origin else ""
    cas_number = clean_text(cas_number) if cas_number else ""

    # Build query parts
    query_parts = []
    if material_name:
        query_parts.append(f"Material Name: {material_name}")
    if material_description:
        query_parts.append(f"Description: {material_description}")
    if material_category:
        query_parts.append(f"Category: {material_category}")
    if material_sub_category:
        query_parts.append(f"Sub category: {material_sub_category}")
    if raw_material_use_class:
        query_parts.append(f"Use class: {raw_material_use_class}")
    if country_of_origin:
        query_parts.append(f"Country of origin: {country_of_origin}")
    if cas_number:
        query_parts.append(f"CAS number: {cas_number}")
    if cas_chemical_name:
        query_parts.append(f"Chemical name: {cas_chemical_name}")

    # Join all into a final query string
    final_query = "; ".join(query_parts)
    return final_query


# src/retrieval/semantic_chapter_predictor.py

def predict_chapters_semantic(query: str, vectorstore, top_n=3):
    """
    Predict top chapters semantically using vector similarity.
    """
    # Step 1: retrieve top 50 documents semantically
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 50}  # retrieve more to get chapter diversity
    )

    retrieved_docs = retriever.invoke(query)

    if not retrieved_docs:
        return []

    # Step 2: count chapter frequency
    chapters = [doc.metadata["chapter_code"] for doc in retrieved_docs]
    top_chapters = [ch for ch, _ in Counter(chapters).most_common(top_n)]

    return top_chapters

from langchain_core.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from src.retrieval.chapter_predictor import get_llm

# def predict_final_hsn(reranked_docs, user_query):
#     llm = get_llm().with_structured_output(HSNResponse)  # AzureChatOpenAI instance

#     # Build candidate HSN string
#     candidate_hsns_str = "\n".join(
#         f"{doc.metadata.get('hsn_6_digit','NA')} - {doc.metadata.get('heading_title','')} (Chapter {doc.metadata.get('chapter_code','')})"
#         for doc in reranked_docs
#     )

#     predicted_chapters_str = ", ".join(
#         sorted({doc.metadata.get('chapter_code','NA') for doc in reranked_docs})
#     )

    # prompt_template = f"""
    # You are an expert in Indian HSN codes. Pick the top 3 HSN codes for a product description.

    # <Product Query>
    # {user_query}
    # </Product Query>

    # <Predicted Chapters>
    # {predicted_chapters_str}
    # </Predicted Chapters>

    # <Candidate HSNs>
    # {candidate_hsns_str}
    # </Candidate HSNs>

    # <RULES>
    # 1. Only select from the candidate HSNs.
    # 2. Do NOT include markdown.
    # 3. Pick HSNs closest semantically to the query and matching predicted chapters.
    # 4. Return the explanation why you predicted this HSN for the query.
    # </RULES>

    # """

    # prompt_template = f"""
    # You are an expert in Indian HSN classification with deep knowledge of tariff rules, material composition, and industrial usage.

    # Your task is to select the TOP 5 most appropriate HSN codes from the provided candidate list.

    # <Product Query>
    # {user_query}
    # </Product Query>

    # <Predicted Chapters>
    # {predicted_chapters_str}
    # </Predicted Chapters>

    # <Candidate HSNs>
    # {candidate_hsns_str}
    # </Candidate HSNs>


    # <INTERNAL REASONING INSTRUCTIONS — DO NOT OUTPUT>
    # 1. Carefully analyze the product query:
    # - Material composition
    # - Function / use
    # - Industry domain
    # - Chemical indicators (CAS, polymer, resin, filler, etc.)

    # 2. Compare each candidate HSN against:
    # - Semantic similarity
    # - Chapter relevance
    # - Specificity vs generality
    # - Inclusion/exclusion logic

    # 3. Rank candidates mentally and identify the best 3 matches.

    # 4. Prefer:
    # - Most specific classification
    # - Correct chapter alignment
    # - Industrial intent match

    # 5. Avoid:
    # - Overly generic codes when specific exists
    # - Codes from unrelated chapters
    # - Duplicates or near-identical categories

    # Perform this reasoning internally step-by-step before producing the final answer.
    # Do NOT reveal your internal reasoning process.
    # </INTERNAL REASONING INSTRUCTIONS>


    # <RULES FOR OUTPUT>
    # 1. Only select from the candidate HSNs provided.
    # 2. Do NOT include markdown formatting.
    # 3. Provide exactly TOP 5 predictions.
    # 4. For each prediction include:
    # - HSN Code
    # - Confidence Score (0–1)
    # - Description
    # - Explanation (clear justification)
    # </RULES FOR OUTPUT>

    # Return the final answer now.
    # """


    # # Build chat prompt
    # chat_prompt = ChatPromptTemplate.from_messages([
    #     SystemMessagePromptTemplate.from_template("You are an expert HSN code picker."),
    #     HumanMessagePromptTemplate.from_template(prompt_template)
    # ])

    # # Format prompt and convert to messages
    # formatted_prompt = chat_prompt.format_prompt()
    # messages = formatted_prompt.to_messages()  # list of BaseMessage objects

    # # Correct AzureChatOpenAI call for this version
    # response = llm.invoke(messages)
    # return response

# LLM call for final HSN prediction with enhanced instructions and few-shots

from pydantic import BaseModel, Field
from typing import List
from src.schema.hsn_schema import FinalHSNOutput


def predict_final_hsn(docs, query, top_k=9):
    llm = get_llm().with_structured_output(FinalHSNOutput)
    context = "\n\n".join([
        f"""
        HSN: {doc.metadata.get('hsn_6_digit')}
        Heading Description: {doc.metadata.get('heading_title')}
        Chapter: {doc.metadata.get('chapter_code')}
        Chapter Description: {doc.metadata.get('chapter_title')}
        Subheading Description: {doc.metadata.get('subheading_title')}
        """
        for doc in docs
    ])

    prompt = f"""
    You are an expert in customs tariff classification.

    <User Query>
    {query}
    </User Query>

    <Candidate HSN Entries>
    {context}
    </Candidate HSN Entries>

    <TASKS>
    1. Analyze the user query carefully.
    2. Compare with candidate HSN entries.
    3. Select the {top_k} most relevant HSN codes.
    4. Rank them from highest to lowest match probability.
    </TASKS>

    <RULES>
    - Prefer chemical composition match over general category.
    - Prefer CAS number match when available.
    - Prefer polymer type and functional use similarity.
    - Do NOT invent new HSN codes.
    - Only choose from the provided candidates.
    </RULES>

    Return structured output.

    """
    
    # Build chat prompt
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template("You are an expert HSN code picker."),
        HumanMessagePromptTemplate.from_template(prompt)
    ])

    # Format prompt and convert to messages
    formatted_prompt = chat_prompt.format_prompt()
    messages = formatted_prompt.to_messages()  # list of BaseMessage objects

    result = llm.invoke(messages)

    return result


