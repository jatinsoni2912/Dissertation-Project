import json
import streamlit.components.v1 as components
from styles import EDINBURGH_CENTER

def render_map(geojson_collection: dict, map_colour: str, height: int = 680,) -> None:
    
    center_lat, center_lon = EDINBURGH_CENTER
    geojson_str = json.dumps(geojson_collection)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>GeoQuery Edinburgh Live Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        html, body, #map {{ height: 100%; margin: 0; padding: 0; background-color: #f4f0e8; }}
        .leaflet-popup-content {{ font-family: 'DM Sans', sans-serif; color: #1a2744; }}
    </style>
</head>