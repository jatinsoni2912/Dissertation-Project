import streamlit as st
import styles
import sidebar
from query_panel import render_query_panel
from map_view import render
from app_utils import EXAMPLE_QUERIES
from query_handler import run_query
from conversations import add_message
import context
from asr import transcribe, asr_available
    
try:
    ASR_ENABLED = asr_available()

except ImportError:
    ASR_ENABLED = False

    def transcribe(*a, **kw):
        return {"text": "", "confidence": 0.0}

st.set_page_config(
    page_title="GeoQuery Edinburgh",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)
styles.apply()

defaults = {
    "query_result":        None,
    "last_query":          "",
    "selected_example":    "",
    "auto_run":            False,
    "show_on_map":         None,
    "map_reset_key":       0,
    "area_filter_active":  False,
    "area_filter_geojson": None,
    "current_user":        None,
    "current_conv_id":     None,
    "current_conv":        None,
    "asr_transcript":      "",
    "asr_confidence":      0.0,
    "pending_asr":         False,
    "input_method":        'text',
    "context_history":     []
    }

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown("""
<div class="geoquery-header">
    <span style="font-size:2.2rem;">🗺️</span>
    <h1 class="geoquery-title">GeoQuery</h1>
</div>
<p class="geoquery-subtitle">
    Ask questions about Edinburgh in plain English — powered by a local LLM and OpenStreetMap data
</p>
""", unsafe_allow_html=True)

sidebar.render_sidebar()

col_left, col_right = st.columns([1, 1.7], gap="large")

user_query, run_btn, model_choice, approach_choice = render_query_panel(
    col_left, asr_enabled=ASR_ENABLED, transcribe_fn=transcribe)

render(col_right)

trigger = run_btn or st.session_state.get('auto_run', False)
st.session_state.auto_run = False

if trigger and user_query.strip():
    st.session_state.show_on_map = None
    with st.spinner("Generating SQL and querying Edinburgh database…"):
        context_loc = context.resolve_location_history(user_query)
        pipeline_query = context.build_context_note(user_query)

        result = run_query(user_query, model_choice, approach_choice, context_loc, pipeline_query)
        
        st.session_state.query_result = result
        st.session_state.last_query = user_query

        context.update_context_history(user_query,
            result.get('location', 'Edinburgh'),
            result.get('results', []),
            result.get('columns', []),
            result.get('is_count', False))

        if st.session_state.get('current_user') and st.session_state.get('current_conv_id'):
            updated = add_message(
                username = st.session_state.current_user,
                conv_id = st.session_state.current_conv_id,
                query = user_query,
                sql = result.get('sql', ''),
                approach = result.get('approach', approach_choice),
                model = result.get('model_used', model_choice),
                row_count = result.get('row_count', 0),
                is_count = result.get('is_count', False),
                fixes_applied = result.get('fixes', []),
                input_method = st.session_state.input_method,
                asr_transcript = st.session_state.asr_transcript or None,
                asr_confidence = st.session_state.asr_confidence or None,
                area_filter_active = st.session_state.get('area_filter_active', False),
                area_filter_geojson = st.session_state.get('area_filter_geojson')
            )
            st.session_state.current_conv = updated
            st.session_state.input_method   = 'text'
            st.session_state.asr_transcript = ''

    st.rerun()
