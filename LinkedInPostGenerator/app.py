import streamlit as st
from main import run_pipeline  # Your existing pipeline

MIN_WORD_LIMIT = 80

st.set_page_config(page_title="LinkedIn Post Generator", layout="centered")
st.title("💡 LinkedIn Post Generator")

# --- Inputs ---
user_role = st.text_input("Describe your role:")
post_idea = st.text_area("Describe your post idea:")
word_limit = st.number_input(
    "Enter word limit (min 80):", 
    min_value=0, 
    value=100, 
    step=50
)

if word_limit < MIN_WORD_LIMIT:
    st.warning(f"⚠️ Word limit must be at least {MIN_WORD_LIMIT}. Please increase it.")
    st.stop()  # Prevent further execution

col1, col2 = st.columns(2)

with col1:
    emoji_level = st.selectbox(
        "Emoji frequency",
        options=["Low", "Medium", "High"],
        index=0  # Default = Low
    )

with col2:
    hashtag_level = st.selectbox(
        "Hashtag frequency",
        options=["Low", "Medium", "High"],
        index=1  # Default = Medium
    )


EMOJI_COUNT_MAP = {
    "Low": 1,
    "Medium": 2,
    "High": 4
}

HASHTAG_COUNT_MAP = {
    "Low": 2,
    "Medium": 4,
    "High": 7
}

emoji_count = EMOJI_COUNT_MAP[emoji_level]
hashtag_count = HASHTAG_COUNT_MAP[hashtag_level]


# --- Generate Button ---
if st.button("Generate Post"):
    if not user_role or not post_idea:
        st.error("Please enter both your role and post idea.")
    else:
        with st.spinner("Generating post..."):
            post = run_pipeline(user_role, post_idea, word_limit, emoji_count, hashtag_count)
        st.success("✅ Post generated successfully!")
        st.text_area("Generated LinkedIn Post", value=post, height=300)
        st.write(f"Word count: {len(post.split())}")
