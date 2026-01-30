import tempfile
import streamlit as st
from loaders.resume_loader import load_resume
from utils.text_cleaner import merge_documents_by_source, clean_resume_text
from utils.result_cleaner import remove_empty_fields
from chains.skill_extraction_chain import get_skill_extraction_chain


st.set_page_config(
    page_title="Resume Skill Extractor",
    page_icon="📄",
    layout="centered"
)

# ---- Custom CSS ----
st.markdown("""
<style>
.skill-card {
    background: linear-gradient(145deg, #0e1117, #161b22);
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 18px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.55);
    border: 1px solid rgba(255,255,255,0.05);
}

/* Force light heading text */
.skill-card h4 {
    color: #E6EDF3 !important;
    font-size: 1.1rem;
    margin-bottom: 12px;
    font-weight: 600;
}

/* Skill tags */
.skill-tag {
    display: inline-block;
    background: linear-gradient(135deg, #7C3AED, #9333EA);
    color: #FFFFFF !important;
    padding: 6px 12px;
    border-radius: 999px;
    margin: 6px 8px 6px 0;
    font-size: 0.85rem;
    font-weight: 500;
    box-shadow: 0 3px 10px rgba(124,58,237,0.4);
}
</style>
""", unsafe_allow_html=True)

# ---- Header ----
st.title("📄 Resume Skill Extractor")
st.caption("AI-powered skill extraction using LangChain")

st.divider()

# ---- Upload ----
uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"],
    help="Supported formats: PDF, DOCX"
)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp:
        tmp.write(uploaded_file.read())
        file_path = tmp.name

    if st.button("🚀 Extract Skills", use_container_width=True):
        with st.spinner("Analyzing resume..."):
            documents = load_resume(file_path)
            merged = merge_documents_by_source(documents)

            resume_text = list(merged.values())[0]
            cleaned_text = clean_resume_text(resume_text)

            chain = get_skill_extraction_chain()
            result = chain.invoke({"resume_text": cleaned_text})

            final_result = remove_empty_fields(result.model_dump())


        st.success("Skills extracted successfully!")

        st.divider()

        # ---- Display Skills ----
        for category, skills in final_result.items():
            st.markdown(
                f"<div class='skill-card'><h4>🧩 {category.replace('_',' ').title()}</h4>",
                unsafe_allow_html=True
            )

            tags_html = ""
            for skill in skills:
                tags_html += f"<span class='skill-tag'>{skill}</span>"

            st.markdown(tags_html + "</div>", unsafe_allow_html=True)
