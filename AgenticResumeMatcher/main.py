from graphs.resume_graph import build_resume_graph
from graphs.master_graph import build_master_graph
from config import *
from utils import *
import os
import time
import warnings
from pathlib import Path

import chromadb

from graphs.resume_graph import build_resume_graph
from graphs.master_graph import build_master_graph
from config import RESUME_FOLDER, JD_FOLDER, CHROMA_COLLECTION, LOG_FILE
from utils import pretty_print_results
# from jd_cache import get_or_create_jd_data

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module="pydantic"
)

RESUME_FOLDER = Path(RESUME_FOLDER)
LOG_FILE = Path(LOG_FILE)

def run_resume_ingestion():
    print("\nChecking resumes folder...")

    resume_graph = build_resume_graph()

    SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt"]

    # Load already processed files
    if LOG_FILE.exists():
        processed = set(line.strip() for line in LOG_FILE.read_text().splitlines())
    else:
        processed = set()

    # Collect only unprocessed resumes
    resume_paths = [
        file for file in RESUME_FOLDER.iterdir()
        if file.suffix.lower() in SUPPORTED_EXTENSIONS
        and file.name not in processed
    ]

        # resume_files = [
    #     os.path.join(RESUME_FOLDER, f)
    #     for f in os.listdir(RESUME_FOLDER)
    #     if f.endswith((".pdf", ".docx"))
    # ]

    print(f"Found {len(resume_paths)} new resumes")

    graph = build_resume_graph()

    for path in resume_paths:
        try:
            graph.invoke({"file_path": str(path)})

            with open(LOG_FILE, "a") as f:
                f.write(path.name + "\n")

            print(f"Processed: {path.name}")
            time.sleep(2)

        except Exception as e:
            print(f"Error processing {path.name}: {e}")

    for file_path in resume_paths:
        resume_graph.invoke({
            "file_path": file_path
        })

    print("Resume ingestion check complete.\n")

def main():

    # Always check resumes first
    run_resume_ingestion()

    # Then ask user for JD search
    user_input = input("Do you want to search for a JD? (yes/no): ").strip().lower()

    if user_input == "yes":
        jd_index = int(input("Enter JD index: ").strip())
        jd_files = sorted(os.listdir(JD_FOLDER))
        selected_jd = jd_files[jd_index]  # change index if needed
        jd_path = os.path.join(JD_FOLDER, selected_jd)
        master_graph = build_master_graph()
        result = master_graph.invoke({
            "input_type": "jd",
            "file_path": jd_path
        })

        pretty_print_results(result["reranked_results"])
    else:
        print("Exiting...")

if __name__ == "__main__":
    main()