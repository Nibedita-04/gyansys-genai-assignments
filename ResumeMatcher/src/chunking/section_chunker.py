import re
from typing import Dict, List, Optional

# Constants
CHUNK_SIZE_RESUME = 300
OVERLAP_RESUME = 60
MIN_WORDS_RESUME = 50

CHUNK_SIZE_JD = 100
OVERLAP_JD = 20
MIN_WORDS_JD = 50

COMMON_RESUME_SECTIONS = [
    "summary", "objective", "skills", "technical skills",
    "experience", "work experience", "projects",
    "education", "certifications", "achievements",
    "internships", "publications", "leadership",
    "extracurricular", "personal details"
]


# Sliding Window Chunker
def sliding_window_chunks(text: str, chunk_size: int, overlap: int, min_words: int) -> List[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if len(chunk.split()) >= min_words:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

# Resume Chunking
def split_resume_sections(text: str) -> Dict[str, str]:
    text_lower = text.lower()
    section_positions = []

    for section in COMMON_RESUME_SECTIONS:
        for match in re.finditer(rf"\b{section}\b", text_lower):
            section_positions.append((match.start(), section))

    section_positions = sorted(section_positions, key=lambda x: x[0])

    if not section_positions:
        return {"full_resume": text}

    sections = {}
    for i, (start, section_name) in enumerate(section_positions):
        end = section_positions[i + 1][0] if i + 1 < len(section_positions) else len(text)
        sections[section_name] = text[start:end].strip()

    return sections


def section_chunk_resume(resume_text: str, resume_metadata: Optional[Dict] = None) -> List[Dict]:
    sections = split_resume_sections(resume_text)
    chunked_output = []

    for section_name, section_text in sections.items():
        section_chunks = sliding_window_chunks(
            section_text, CHUNK_SIZE_RESUME, OVERLAP_RESUME, MIN_WORDS_RESUME
        )
        for i, chunk in enumerate(section_chunks):
            chunked_output.append({
                "text": chunk,
                "metadata": {
                    **(resume_metadata or {}),
                    "section": section_name,
                    "chunk_index": i
                }
            })

    return chunked_output


# JD Chunking (Simple Recursive)
def chunk_job_description(jd_text: str, chunk_size: int = CHUNK_SIZE_JD, overlap: int = OVERLAP_JD) -> List[Dict]:
    """
    Split JD into overlapping chunks without section-wise logic.
    """
    jd_text_clean = jd_text.replace("\r", "").strip()
    chunks = sliding_window_chunks(jd_text_clean, chunk_size, overlap, min_words=MIN_WORDS_JD)
    return [{"text": chunk, "chunk_index": idx} for idx, chunk in enumerate(chunks)]
