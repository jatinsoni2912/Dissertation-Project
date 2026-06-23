import streamlit as st
from styles import APP_CSS

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


col_left, col_right = st.columns([1, 1.7], gap="large")

with col_left:
    st.markdown(
        '<div class="placeholder-box">Query panel will go here<br>'
        '(input box, selectors, search button)</div>',
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown(
        '<div class="placeholder-box">Map will go here</div>',
        unsafe_allow_html=True,
    )