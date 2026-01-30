import os
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_core.documents import Document

def load_resume(file_path: str) -> list[Document]:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".docx":
        loader = Docx2txtLoader(file_path)
        documents = loader.load()

    elif ext == ".pdf":
        loader = PyPDFLoader(file_path)
        documents = loader.load()

    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    return documents


def load_resumes_from_folder(
    folder_path: str,
    max_resumes: int | None = None
) -> list[Document]:

    all_docs: list[Document] = []
    count = 0

    for file in os.listdir(folder_path):

        if max_resumes is not None and count >= max_resumes:
            break

        if file.endswith((".pdf", ".docx")):
            file_path = os.path.join(folder_path, file)
            docs = load_resume(file_path)
            all_docs.extend(docs)
            count += 1

    return all_docs
