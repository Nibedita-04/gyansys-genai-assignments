from loaders.resume_loader import load_resumes_from_folder
from utils.text_cleaner import merge_documents_by_source, clean_resume_text
from chains.skill_extraction_chain import get_skill_extraction_chain
from utils.result_cleaner import remove_empty_fields

RESUME_FOLDER = "data/resumes"
MAX_RESUMES_TO_PARSE = 5  

def main():
    print("Loading resumes...")
    documents = load_resumes_from_folder(
        RESUME_FOLDER,
        max_resumes=MAX_RESUMES_TO_PARSE
    )

    print("Merging resume pages...")
    merged_docs = merge_documents_by_source(documents)

    print("Initializing skill extraction chain...")
    chain = get_skill_extraction_chain()

    print("\nStarting resume parsing...\n")

    for idx, (source, text) in enumerate(merged_docs.items(), start=1):
        print("=" * 100)
        print(f"Resume {idx}")
        print(f"Source: {source}")

        cleaned_text = clean_resume_text(text)

        try:
            result = chain.invoke({"resume_text": cleaned_text})
            cleaned_result = remove_empty_fields(result.model_dump())

            print("Extracted Skills:")
            print(cleaned_result)

        except Exception as e:
            print(f"Error processing {source}: {e}")

    print("\n✅ Resume parsing completed.")


if __name__ == "__main__":
    main()

