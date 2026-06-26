import streamlit as st
from styles import EXAMPLE_QUERIES

from app_utils import conversational_response, generate_follow_ups, feature_label


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

def render_error_if_any(res):
    if res.get('error'):
        st.error(f"Database/Validation Error: {res['error']}")
        

def render_conversational_summary(res, last_query):
    msg = conversational_response(res, last_query)
    st.markdown(
        f'<div style="background:white;border-left:4px solid #c9a84c;'
        f'border-radius:0 10px 10px 0;padding:0.85rem 1rem;margin-bottom:0.75rem;'
        f'font-size:0.95rem;color:#1a2744;box-shadow:0 1px 4px rgba(26,39,68,0.07)">'
        f'🗺️ {msg}</div>', unsafe_allow_html=True,)

def render_area_filter_notice():
    if st.session_state.get('area_filter_active'):
        st.info("📍 Results clipped to drawn area — clear filter to search all of Edinburgh.")

def render_info_pills(res):
    pills = ""

    if res.get('ontology_used'):
        pills += '<span class="info-pill">🧠 Ontology</span>'

    for term in res.get('activity_terms', []):
        pills += f'<span class="info-pill">🏷 {term}</span>'

    if res.get('location'):
        pills += f'<span class="info-pill">📍 {res["location"]}</span>'

    if res.get('approach'):
        pills += f'<span class="info-pill">⚙ {res["approach"]}</span>'

    if pills:
        st.markdown(pills, unsafe_allow_html=True)


def render_map_prompt_or_status(res, row_count):
    if row_count > 0 and st.session_state.show_on_map is None:
        render_map_prompt()
   
    elif st.session_state.show_on_map is True:
        render_map_status()

def render_map_prompt():
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗺️ Show on map", key="show_yes", use_container_width=True):
            st.session_state.show_on_map = True
            st.rerun()
    with c2:
        if st.button("Skip map", key="show_no", use_container_width=True):
            st.session_state.show_on_map = False
            st.rerun()

def render_map_status():
    col_m, col_h = st.columns([3, 1])
    
    with col_m:
        st.success("✓ Results shown on map")
    
    with col_h:
        if st.button("Hide", key="hide_map", use_container_width=True):
            st.session_state.show_on_map = None
            st.rerun()

def render_followup_suggestions(res, last_query):
    st.markdown("**You might also want to ask:**")
    follow_ups = generate_follow_ups(res, last_query)

    fu_cols = st.columns(len(follow_ups))
    for i, sug in enumerate(follow_ups):
        with fu_cols[i]:
            lbl = sug[:40] + ("…" if len(sug) > 40 else "")
            if st.button(lbl, key=f"fu_{i}", use_container_width=True, help=sug):
                st.session_state.selected_example = sug
                st.session_state.input_method     = 'text'
                st.session_state.pending_asr      = False
                st.session_state.asr_transcript   = ''
                st.session_state.auto_run         = True
                st.rerun()









































































































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
