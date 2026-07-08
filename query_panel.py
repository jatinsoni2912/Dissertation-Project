import streamlit as st
from styles import EXAMPLE_QUERIES

from app_utils import conversational_response, generate_follow_ups, feature_label
from audio_recorder_streamlit import audio_recorder

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

def render_followup_input(row_count, is_count):
    st.markdown("")
    
    followup_val = st.text_input("Or ask a follow-up question…", value="",
        placeholder="e.g. What about near Leith?",
        key=f"followup_{row_count}_{is_count}",)

    col_fu, col_new = st.columns([2, 1])

    with col_fu:
        if st.button("➤ Ask follow-up", key="ask_followup",
                     use_container_width=True, disabled=not followup_val.strip()):
            
            st.session_state.selected_example = followup_val.strip()
            st.session_state.input_method     = 'text'
            st.session_state.pending_asr      = False
            st.session_state.asr_transcript   = ''
            st.session_state.auto_run         = True
            st.rerun()

    with col_new:

        if st.button("✦  New query", key="new_query", use_container_width=True):
            reset_query_state()
            st.rerun()
    

def reset_query_state():
    for k in ('query_result', 'show_on_map', 'selected_example',
              'last_query', 'pending_asr', 'asr_transcript', 'context_history'):
        
        st.session_state[k] = (
            None if k in ('query_result', 'show_on_map')
            else [] if k == 'context_history'
            else False if k == 'pending_asr'
            else ''
        )
    
    st.session_state.input_method = 'text'


def render_technical_details(res, row_count, is_count):
    with st.expander("🔧 Technical details", expanded=False):

        if res.get('fixes'):
            fixes_html = "".join(
                f'<span class="fix-tag">{f}</span>' for f in res['fixes']
            )
            st.markdown(f"**Fixes applied:**<br>{fixes_html}", unsafe_allow_html=True)

        st.markdown("**Generated SQL:**")
        st.markdown(
            f'<div class="sql-expander">{res.get("sql", "")}</div>',
            unsafe_allow_html=True,
        )

        if res.get('results') and not is_count and row_count > 0:
            render_results_table(res, row_count)


def render_results_table(res, row_count):
    st.markdown(f"**Results table** ({min(row_count, 10)} of {row_count}):")

    display_rows = []
    for row in res['results'][:10]:
        dr = {
            c: row[i]
            for i, c in enumerate(res.get('columns', []))
            if c not in ('geometry', 'st_asgeojson', 'geom', 'way')
            and row[i] is not None
        }
        if dr:
            display_rows.append(dr)

    if display_rows:
        st.dataframe(display_rows, use_container_width=True, hide_index=True)


def show_result_panel(res, last_query):
    row_count = res.get('row_count', 0)
    is_count  = res.get('is_count', False)

    render_error_if_any(res)
    render_conversational_summary(res, last_query)
    render_area_filter_notice()

    render_info_pills(res)

    render_map_prompt_or_status(res, row_count)

    render_followup_suggestions(res, last_query)
    render_followup_input(row_count, is_count)

    render_technical_details(res, row_count, is_count)

def render_area_filter_controls():
    if st.session_state.get("area_filter_active"):
        colf, colc = st.columns([3, 1])

        with colf:
            st.info("📍 Area filter active — results will be clipped to drawn area")

        with colc:
            if st.button("✕ Clear", key="clear_area_btn", use_container_width=True):
                st.session_state.area_filter_geojson = None
                st.session_state.area_filter_active = False
                st.session_state.map_reset_key += 1
                st.rerun()

def capture_audio_bytes():
    try:
        audio_bytes = audio_recorder(text="", icon_size="2x", recording_color="#e84e4e", neutral_color="#6aa36f", key="mic_recorder")

        if audio_bytes and len(audio_bytes) > 1000:
            return audio_bytes

    except ImportError:
        st.caption("Install audio-recorder-streamlit to enable voice input.")

    return None

def render_asr():
    conf = st.session_state.asr_confidence
    color = "#2d8a4e" if conf >= 0.7 else "#c47a1a"

    st.markdown(
        f'<div style="background:#f0f4f0;border-left:3px solid {color};'
        f'padding:8px;border-radius:4px;margin:6px 0">'
        f'<b>Heard:</b> {st.session_state.asr_transcript}<br>'
        f'<small style="color:{color}">Confidence: {conf:.0%}</small></div>',
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("✓ Use this", use_container_width=True):
            st.session_state.selected_example = st.session_state.asr_transcript
            st.session_state.pending_asr = False
            st.rerun()

    with col_b:
        if st.button("✗ Discard", use_container_width=True):
            st.session_state.asr_transcript = ""
            st.session_state.pending_asr = False
            st.session_state.input_method = "text"
            st.rerun()

def render_voice_input(asr_enabled, transcribe_fn):
    if not asr_enabled:
        return

    st.markdown("**Or speak your query:**")

    audio_bytes = capture_audio_bytes()

    if audio_bytes:
        with st.spinner("Transcribing..."):
            result = transcribe_fn(audio_bytes)

        if result.get("text"):
            st.session_state.asr_transcript = result["text"]
            st.session_state.asr_confidence = result["confidence"]
            st.session_state.pending_asr = True
            st.session_state.input_method = "voice"

    if st.session_state.get("pending_asr"):
        render_asr()

def render_query_panel(asr_enabled=False, transcribe_fn=None):
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

    if asr_enabled:
        render_voice_input(asr_enabled, transcribe_fn)

    render_area_filter_controls()

    run_btn = st.button("🔍  Search", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.query_result:
            st.markdown("**Try an example:**")
            cols = st.columns(2)
            for i, example in enumerate(EXAMPLE_QUERIES):
                with cols[i % 2]:
                    label = example[:38] + ("…" if len(example) > 38 else "")
                    if st.button(label, key=f"ex_{i}", use_container_width=True):
                        st.session_state.selected_example = example
                        st.rerun()
    
    if st.session_state.query_result:
            res = st.session_state.query_result
            st.markdown("---")
            show_result_panel(res, st.session_state.get('last_query', ''))
        
    return user_query, run_btn, user_query, model_choice, approach_choice
