import re
from collections import defaultdict

def merge_documents_by_source(documents):
    merged = defaultdict(str)

    for doc in documents:
        source = doc.metadata.get("source", "unknown")
        merged[source] += "\n" + doc.page_content

    return merged

def clean_resume_text(text: str) -> str:
    text = re.sub(r"[•▪●■◦]", " ", text)

    text = re.sub(r"\n+", "\n", text)

    text = re.sub(r"\s+", " ", text)

    text = re.sub(r"Page\s+\d+\s+of\s+\d+", "", text, flags=re.IGNORECASE)

    return text.strip()