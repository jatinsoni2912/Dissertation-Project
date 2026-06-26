import streamlit as st
from styles import EXAMPLE_QUERIES

def show_conversation_history():
    conv = st.session_state.get('current_conv')
    if not conv or not conv.get('messages'):
        return
    with st.container():
        for msg in conv['messages']:
            badge  = "🎤" if msg.get('input_method') == 'voice' else "⌨️"
            rc     = msg.get('row_count', 0)
            rc_txt = f"COUNT: {rc}" if msg.get('is_count') else f"{rc} result(s)"
            st.markdown(
                f'<div style="background:#f7f7f7;border-left:3px solid #6aa36f;'
                f'padding:8px 10px;border-radius:4px;margin-bottom:6px;font-size:0.9em">'
                f'<b>{badge} {msg["query"]}</b><br>'
                f'<span style="color:#666">{rc_txt} · {msg["approach"]}</span></div>',
                unsafe_allow_html=True,
            )
    st.markdown("---")

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
