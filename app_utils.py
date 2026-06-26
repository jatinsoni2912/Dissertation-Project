import json
import re
import streamlit as st


EDINBURGH_CENTER = [55.9533, -3.1883]

EXAMPLE_QUERIES = [
    "Where can I go cycling in Edinburgh?",
    "Find parks near the city centre",
    "How many post offices are in Edinburgh?",
    "Where can I walk my dog near Leith?",
    "Find cafes within 500 metres of Princes Street",
    "Show me swimming pools in Edinburgh",
    "Find restaurants in Stockbridge",
    "Where can I play football near Newington?",
]

FEATURE_COLOURS = {
    'park':          '#2d6a4f',
    'garden':        '#40916c',
    'cycleway':      '#e07b39',
    'footway':       '#6b8f71',
    'path':          '#6b8f71',
    'cafe':          '#c9a84c',
    'restaurant':    '#c9a84c',
    'pub':           '#9b6b3a',
    'post_office':   '#1a2744',
    'library':       '#4a5568',
    'museum':        '#7c5cbf',
    'swimming_pool': '#3a86ff',
    'pitch':         '#52b788',
    'track':         '#52b788',
    'sports_centre': '#52b788',
    'golf_course':   '#95d5b2',
    'parking':       '#adb5bd',
    'default':       '#c9a84c',
}

def get_feature_colour(sql):
    sql_l = sql.lower()
    for tag, colour in FEATURE_COLOURS.items():
        if f"'{tag}'" in sql_l or f'"{tag}"' in sql_l:
            return colour
    return FEATURE_COLOURS['default']

def parse_geojson(raw):
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None