import streamlit as st
import os
from graphs.resume_graph import build_resume_graph
from graphs.master_graph import build_master_graph
from config import RESUME_FOLDER

# Initialize graphs once
resume_graph = build_resume_graph()
master_graph = build_master_graph()

st.set_page_config(page_title="Agentic Resume Matcher", layout="wide")

st.title("📄 Agentic Resume Matcher")
st.markdown("Automatically ingest resumes and match them against a Job Description.")

# -----------------------------
# Resume Ingestion Section
# -----------------------------

st.header("1️⃣ Resume Ingestion")

if st.button("Check & Ingest Resumes"):
    resume_files = [
        os.path.join(RESUME_FOLDER, f)
        for f in os.listdir(RESUME_FOLDER)
        if f.endswith((".pdf", ".docx"))
    ]

    progress = st.progress(0)
    total = len(resume_files)

    for i, file_path in enumerate(resume_files):
        resume_graph.invoke({"file_path": file_path})
        progress.progress((i + 1) / total)

    st.success("Resume ingestion complete! ✅")

# -----------------------------
# JD Upload & Search Section
# -----------------------------

st.header("2️⃣ Upload Job Description")

uploaded_jd = st.file_uploader("Upload JD (.pdf or .docx)", type=["pdf", "docx"])

if uploaded_jd:
    jd_path = os.path.join("data/jds", uploaded_jd.name)

    with open(jd_path, "wb") as f:
        f.write(uploaded_jd.getbuffer())

    st.success("JD uploaded successfully!")

    if st.button("Run Matching"):
        with st.spinner("Running matching pipeline..."):
            result = master_graph.invoke({
                "input_type": "jd",
                "file_path": jd_path
            })

        st.header("🏆 Top Matching Candidates")

        reranked = result.get("reranked_results", [])

        if not reranked:
            st.warning("No results found.")
        else:
            for i, candidate in enumerate(reranked[:5], start=1):
                with st.expander(f"Rank #{i} — Final Score: {round(candidate['final_score'], 3)}"):
                    st.write("**Experience (yrs):**", candidate["metadata"]["experience"])
                    st.write("**Skills:**", candidate["metadata"]["skills"])
                    st.write("**Semantic Score:**", round(candidate["semantic_score"], 3))
                    st.write("**Experience Score:**", candidate["experience_score"])
                    st.write("**Skill Score:**", candidate["skill_score"])
                    st.write("**Penalty:**", candidate["underqualification_penalty"])
                    st.markdown("**Resume Preview:**")
                    st.write(candidate["document"])