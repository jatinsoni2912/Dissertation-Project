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
<body>
    <div id="map"></div>
    <script>
        var edinburghBounds = L.latLngBounds(
            L.latLng(55.85, -3.40), L.latLng(56.00, -3.00)
        );

        var map = L.map('map', {{
            preferCanvas: true, maxBounds: edinburghBounds,
            maxBoundsViscosity: 1.0, minZoom: 11, maxZoom: 18,
            zoomSnap: 0.5, wheelPxPerZoomLevel: 120,
        }}).setView([{center_lat}, {center_lon}], 13);

        map.on('zoomend', function() {{
            if (map.getZoom() < 11) map.setZoom(11, {{ animate: false }});
        }});

        var osm = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);

        var cartoLight = L.tileLayer(
            'https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png',
            {{ attribution: '© CartoDB' }}
        );

        L.control.layers(
            {{ "OpenStreetMap": osm, "Light (CartoDB)": cartoLight }},
            null, {{ position: 'topright' }}
        ).addTo(map);

        var geojsonData     = {geojson_str};
        var highlightColour = "{map_colour}";

        if (geojsonData && geojsonData.features && geojsonData.features.length > 0) {{
            var featureLayer = L.geoJSON(geojsonData, {{
                pointToLayer: function(feature, latlng) {{
                    return L.circleMarker(latlng, {{
                        radius: 8, fillColor: highlightColour, color: highlightColour,
                        weight: 2, opacity: 1, fillOpacity: 0.85,
                    }});
                }},

                style: function(feature) {{
                    var t = feature.geometry.type;
                    if (t === 'LineString' || t === 'MultiLineString')
                        return {{ color: highlightColour, weight: 4, opacity: 0.85 }};
                    return {{ fillColor: highlightColour, color: highlightColour,
                              weight: 2, fillOpacity: 0.45 }};
                }},

                onEachFeature: function(feature, layer) {{
                    var name = feature.properties.name || "Unnamed Feature";
                    layer.bindTooltip(name);
                    layer.bindPopup("<b>" + name + "</b>");
                }},

            }}).addTo(map);



                   }}

    </script>
</body>   
</html> """