import streamlit as st
import styles
import sidebar
from query_panel import render_query_panel
from map_view import render_map

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
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown("""
<div class="geoquery-header">
    <span style="font-size:2.2rem;">🗺️</span>
    <h1 class="geoquery-title">GeoQuery Edinburgh</h1>
</div>
<p class="geoquery-subtitle">
    Ask questions about Edinburgh in plain English — powered by a local LLM and OpenStreetMap data
</p>
""", unsafe_allow_html=True)

sidebar.render_sidebar()

col_left, col_right = st.columns([1, 1.7], gap="large")

with col_left:
    st.markdown('<div class="query-card">', unsafe_allow_html=True)
    model_choice = st.selectbox(
        "LLM Model", options=["qwen2.5-coder:1.5b"], index=0,
    )
    approach_choice = st.selectbox(
        "Query Approach",
        options=["Approach 1 — LLM only", "Approach 2 — LLM + MCP"],
        index=0,
    )
    user_query = st.text_input(
        "Ask a question about Edinburgh",
        value=st.session_state.selected_example,
        placeholder="e.g. Where can I go cycling near Leith?",
        label_visibility="collapsed",
    )