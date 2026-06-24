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

    approach_choice = st.selectbox(
        "Query Approach",
        options=["Approach 1 — LLM only", "Approach 2 — LLM + MCP"],
        index=0,
        help=("Approach 1 uses static schema injection. "
              "Approach 2 uses the Postgres MCP server for live schema access."),
    )

    user_query = st.text_input(
        "Ask a question about Edinburgh",
        placeholder="e.g. Where can I go cycling near Leith?",
        label_visibility="collapsed",
    )

    run_btn = st.button("🔍  Search", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("**Try an example:**")
    cols = st.columns(2)
    for i, example in enumerate(EXAMPLE_QUERIES):
        with cols[i % 2]:
            label = example[:38] + ("…" if len(example) > 38 else "")
            st.button(label, key=f"ex_{i}", use_container_width=True)

    return run_btn, user_query, approach_choice, model_choice
