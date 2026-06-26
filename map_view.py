import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

from utils import FEATURE_COLOURS, get_feature_colour
from styles import EDINBURGH_CENTER

EDINBURGH_BOUNDS = [[55.85, -3.40], [56.00, -3.00]]

def build_base_map():
    map = folium.Map(
        location=EDINBURGH_CENTER,
        zoom_start=13,
        prefer_canvas=True,
        tiles=None,
        control_scale=False,
    )
    
    map.options['maxBounds']           = EDINBURGH_BOUNDS
    map.options['maxBoundsViscosity']  = 1.0
    map.options['minZoom']             = 11
    map.options['maxZoom']             = 18
    map.options['zoomSnap']            = 0.5
    map.options['wheelPxPerZoomLevel'] = 120

    folium.TileLayer(tiles='cartodbpositron', name='Light (CartoDB)', attr='© CartoDB', control=True, show=False,).add_to(map)
    folium.TileLayer(tiles='OpenStreetMap', name='OpenStreetMap', attr='© OpenStreetMap contributors', control=True, show=True,).add_to(map)
    folium.LayerControl(position='topright').add_to(map)
    
    return map

def add_draw_controls(m):
    Draw(position='topleft', 
         draw_options={'polyline': False, 'circle': False, 'marker': False, 'circlemarker': False,
                       
                       'polygon': {
                           'allowIntersection': False, 'showArea': True,
                           'shapeOptions': {'color': '#c9a84c', 'fillOpacity': 0.15},},
                        
                        'rectangle': {'shapeOptions': {'color': '#c9a84c', 'fillOpacity': 0.15},},},
        
        edit_options={'edit': True, 'remove': True},).add_to(m)

def split_features_by_geometry(features):
    points, lines, polygons = [], [], []

    for feat in features:
        feat.setdefault('properties', {}).setdefault('name', 'Unnamed Feature')
        
        t = feat.get('geometry', {}).get('type', '')

        if t == 'Point':
            points.append(feat)
        
        elif t in ('LineString', 'MultiLineString'):
            lines.append(feat)
        
        else:
            polygons.append(feat)

    return points, lines, polygons    

def build_interaction_elements():
    tooltip = folium.GeoJsonTooltip(fields=['name'], aliases=[''])
    popup = folium.GeoJsonPopup(fields=['name'], aliases=[''])

    return tooltip, popup

def add_point_layer(fg, points, colour, tooltip, popup):
    if not points:
        return

    folium.GeoJson({"type": "FeatureCollection", "features": points}, name='Points',
        marker=folium.CircleMarker(radius=8, color=colour, fill_color=colour,weight=2, fill_opacity=0.85,),
        tooltip=tooltip, popup=popup,).add_to(fg)

def add_line_layer(fg, lines, colour, tooltip, popup):
    if not lines:
        return

    folium.GeoJson({"type": "FeatureCollection", "features": lines},name='Lines',
        style_function=lambda f, c=colour: {'color': c, 'weight': 4, 'opacity': 0.85,}, tooltip=tooltip, popup=popup,).add_to(fg)

def add_polygon_layer(fg, polygons, colour, tooltip, popup):
    if not polygons:
        return

    folium.GeoJson({"type": "FeatureCollection", "features": polygons},name='Polygons',
        style_function=lambda f, c=colour: {'fillColor': c, 'color': c, 'weight': 2, 'fillOpacity': 0.45,}, tooltip=tooltip, popup=popup,).add_to(fg)

def build_results_layer(geojson_collection, colour):

    fg = folium.FeatureGroup(name='Query results')
    features = geojson_collection.get('features', [])

    if not features:
        return fg, False

    points, lines, polygons = split_features_by_geometry(features)
    tooltip, popup = build_interaction_elements()

    add_point_layer(fg, points, colour, tooltip, popup)
    add_line_layer(fg, lines, colour, tooltip, popup)
    add_polygon_layer(fg, polygons, colour, tooltip, popup)

    return fg, True

def initialise_map_state():
    colour = FEATURE_COLOURS['default']
    geojson_collection = {"type": "FeatureCollection", "features": []}

    if st.session_state.query_result:
        res = st.session_state.query_result
        colour = get_feature_colour(res.get('sql', ''))

        if st.session_state.show_on_map:
            geojson_collection = res.get('geojson_data', {"type": "FeatureCollection", "features": []})

    return colour, geojson_collection

def fit_map_to_results(base_map, geojson_collection):
    try:
        bounds = folium.GeoJson(geojson_collection).get_bounds()
        if bounds and bounds[0][0] is not None:
            base_map.fit_bounds(bounds, padding=(30, 30))
    except Exception:
        pass
