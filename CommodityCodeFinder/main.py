from src.retrieval.reranker import rerank
from src.ingestion.vectordb import get_vectorstore
from src.retrieval.chapter_predictor import predict_final_hsn, predict_chapters_semantic, generate_query

def get_available_chapters(vectorstore):
    """
    Dynamically extract available chapters from indexed metadata.
    """
    all_data = vectorstore.get(include=["metadatas"])
    chapters = sorted(
        list(set(meta["chapter_code"] for meta in all_data["metadatas"]))
    )
    return chapters



def normalize_hsn(code: str) -> str:
    """
    Convert any HSN format to clean 6-digit numeric string.
    Example:
        2803 00 10 → 280300
        28030010 → 280300
        2803.00.10 → 280300
    """
    if not code:
        return ""

    code = str(code)
    code = code.replace(" ", "").replace(".", "").replace("-", "")
    return code[:6]




from src.retrieval.reranker import rerank
from src.ingestion.vectordb import get_vectorstore
from src.retrieval.chapter_predictor import (
    predict_final_hsn,
    predict_chapters_semantic,
    generate_query
)



import pandas as pd

"""TRIAL-7: FINAL VERSION WITH 
Retrieves 30–40 docs per predicted chapter

Forms a total pool of ~90–120 docs

Computes hybrid score = similarity + chapter weighting

Sends top 25–40 docs to LLM

LLM outputs top 10 final HSNs

Metrics for Chapter Accuracy, Retrieval@90–120, Top@30, Final@10"""
def main():

    csv_path = "data/inputs.csv"
    df = pd.read_csv(csv_path)

    ground_truth = [
        39079990, 38249900, 25174100, 39023000, 39023000, 39111090,
        39022000, 27122010, 3204200000, 39029090, 390230, 39014090,
        29319090, 28030010, 38123990, 3911100000, 28030010, 28365000,
        39069090, 39069090, 25111000, 32041700, 35069190, 35069190,
        2803000010, 28030010, 29319090, 38249992, 2710191000, 3901901000
    ]

    # ============================
    # Metrics counters
    # ============================
    total_rows = 0
    chapter_found_count = 0
    retrieval_found_count = 0
    top30_found_count = 0
    final_found_count = 0

    id_counter = 1

    # ============================
    # Load resources ONCE
    # ============================
    vectorstore = get_vectorstore()
    available_chapters = get_available_chapters(vectorstore)

    for idx, row in df.iterrows():

        print("\n==============================")
        print(f"Row {id_counter}: Processing...")
        print("==============================")

        # ============================
        # Read columns safely
        # ============================
        material_description = str(row.get("Material Description", "")).strip()
        material_name = str(row.get("Material Name", "")).strip()
        material_category = str(row.get("Material Category", "")).strip()
        material_sub_category = str(row.get("Material Sub category", "")).strip()
        raw_material_use_class = str(row.get("Raw Material Use Class", "")).strip()
        cas_number = str(row.get("CAS number", "")).strip()
        country_of_origin = str(row.get("Country of origin", "")).strip()

        # ============================
        # Ground truth
        # ============================
        ground_truth_raw = str(ground_truth[id_counter - 1])
        gt_6 = normalize_hsn(ground_truth_raw)
        gt_chapter = gt_6[:2]  # first 2 digits for chapter

        # ============================
        # Generate Query
        # ============================
        query = generate_query(
            material_description,
            material_name,
            material_category,
            material_sub_category,
            raw_material_use_class,
            cas_number,
            country_of_origin
        )

        if not query:
            print("Query cannot be empty.")
            continue

        # ============================
        # Chapter Prediction
        # ============================
        predicted = predict_chapters_semantic(query, vectorstore, top_n=5)
        print("Predicted Chapters:", predicted)

        if not predicted:
            predicted = available_chapters

        # ============================
        # Retrieval per chapter (30–40 docs)
        # ============================
        all_docs = []

        for chapter in predicted:
            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 30,  # 30–40 per chapter
                    "filter": {"chapter_code": chapter}
                }
            )
            docs = retriever.invoke(query)
            if docs:
                all_docs.extend(docs)

        if not all_docs:
            print("No documents retrieved.")
            id_counter += 1
            continue

        # ============================
        # Chapter Retrieval check
        # ============================
        chapter_found = gt_chapter in predicted
        if chapter_found:
            chapter_found_count += 1

        # ============================
        # Hybrid Scoring
        # ============================
        scored_docs = []
        for doc in all_docs:
            sim_score = getattr(doc, "score", 0)
            chapter_score = 1.0 if doc.metadata.get("chapter_code") in predicted else 0.0
            hybrid_score = 0.6 * sim_score + 0.4 * chapter_score
            scored_docs.append((doc, hybrid_score))

        # Sort by hybrid score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # Extract docs only
        all_docs = [doc for doc, score in scored_docs]


        # ============================
        # Retrieval@90–120
        # ============================
        retrieval_pool = all_docs[:120]  # total pool
        retrieval_hsns = [normalize_hsn(doc.metadata.get("hsn_6_digit", "")) for doc in retrieval_pool]
        retrieval_found = gt_6 in retrieval_hsns
        if retrieval_found:
            retrieval_found_count += 1

        # ============================
        # Rerank Top 25–40 and check Top@30
        # ============================
        top_for_llm = retrieval_pool[:]  # send 25–40 to LLM
        reranked_docs = rerank(query, top_for_llm, top_k=30)
        reranked_hsns = [normalize_hsn(doc.metadata.get("hsn_6_digit", "")) for doc in reranked_docs]
        top30_found = gt_6 in reranked_hsns
        if top30_found:
            top30_found_count += 1

        # ============================
        # Final Prediction using LLM (top 10)
        # ============================
        final_hsn = predict_final_hsn(retrieval_pool[:], query)
        final_hsn_list = [normalize_hsn(pred.hsn) for pred in final_hsn.predictions if pred.hsn]
        final_found = gt_6 in final_hsn_list
        if final_found:
            final_found_count += 1

        # ============================
        # Print row summary
        # ============================
        print(f"\nGT Chapter: {gt_chapter}")
        print(f"Chapter Retrieval@5: {'FOUND' if chapter_found else 'NOT FOUND'}")
        print(f"Retrieval@150: {'FOUND' if retrieval_found else 'NOT FOUND'}")
        # print(f"Top@30: {'FOUND' if top30_found else 'NOT FOUND'}")
        print(f"Final@10: {'FOUND' if final_found else 'NOT FOUND'}")

        print("\nFINAL PREDICTION")
        print("------------------------------")
        for pred in final_hsn.predictions:
            print(pred.hsn)

        id_counter += 1
        total_rows += 1

    # ============================
    # Final Metrics
    # ============================
    print("\n==============================")
    print("FINAL METRICS")
    print("==============================")
    print(f"Chapter Accuracy@5: {chapter_found_count / total_rows:.2%}")
    print(f"Retrieval@150: {retrieval_found_count / total_rows:.2%}")
    # print(f"Top@30: {top30_found_count / total_rows:.2%}")
    print(f"Final@10: {final_found_count / total_rows:.2%}")
    print(f"Processed {total_rows} rows")
    print("==============================\n")


if __name__ == "__main__":
    main()
