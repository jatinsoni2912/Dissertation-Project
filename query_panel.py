import streamlit as st
from styles import EXAMPLE_QUERIES

def render_query_panel() -> tuple[bool, str, str, str]:
    st.markdown('<div class="query-card">', unsafe_allow_html=True)

    model_choice = st.selectbox(
        "LLM Model",
        options=["qwen2.5-coder:1.5b"],
        index=0,
        help="Select which locally deployed model to use for SQL generation",
    )