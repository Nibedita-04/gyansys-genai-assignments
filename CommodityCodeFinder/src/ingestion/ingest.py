from src.ingestion.vectordb import get_vectorstore
from src.ingestion.flatten import flatten_chapters
import time
from openai import RateLimitError


def ingest_records(records, batch_size=20):
    """
    Ingest flattened records into Chroma vector database in batches.
    """

    vectorstore = get_vectorstore()
    total = len(records)

    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]

        texts = [r["text"] for r in batch]
        metadatas = [r["metadata"] for r in batch]
        ids = [r["id"] for r in batch]

        print(f"Ingesting batch {i} to {i + len(batch)}")

        success = False
        retries = 0

        while not success and retries < 5:
            try:
                vectorstore.add_texts(
                    texts=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                success = True

            except RateLimitError:
                wait_time = 5 * (retries + 1)
                print(f"Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1

        time.sleep(3)  # safety pause between batches

    print("Ingestion complete")


# --------------------------------------------------
# Execution block
# --------------------------------------------------

if __name__ == "__main__":

    print("Flattening data from data/raw ...")
    records = flatten_chapters("data/raw")

    print(f"Total flattened records: {len(records)}")

    print("Starting ingestion...\n")

    ingest_records(records)

    print("\nAll chapters ingested successfully 🚀")
