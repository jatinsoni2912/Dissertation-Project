import streamlit as st
from styles import APP_CSS, FEATURE_COLOURS
from sidebar import render_sidebar
from query_panel import render_query_panel
from map_view import render_map

st.set_page_config(
    page_title="GeoQuery Edinburgh",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(APP_CSS, unsafe_allow_html=True)

st.markdown("""
<div class="geoquery-header">
    <span style="font-size:2.2rem;">🗺️</span>
    <h1 class="geoquery-title">GeoQuery Edinburgh</h1>
</div>
<p class="geoquery-subtitle">
    Ask questions about Edinburgh in plain English — powered by a local LLM and OpenStreetMap data
</p>
""", unsafe_allow_html=True)

render_sidebar()

col_left, col_right = st.columns([1, 1.7], gap="large")

with col_left:
    run_btn, user_query, model_choice, approach_choice = render_query_panel()

with col_right:
    empty_geojson = {"type": "FeatureCollection", "features": []}
    render_map(
        geojson_collection = empty_geojson,
        map_colour         = FEATURE_COLOURS['default'],
    )