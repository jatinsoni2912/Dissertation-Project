import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

from utils import FEATURE_COLOURS, get_feature_colour
from styles import EDINBURGH_CENTER

EDINBURGH_BOUNDS = [[55.85, -3.40], [56.00, -3.00]]

def build_base_map():
    m = folium.Map(
        location=EDINBURGH_CENTER,
        zoom_start=13,
        prefer_canvas=True,
        tiles=None,
        control_scale=False,
    )


