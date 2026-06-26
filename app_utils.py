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

def prepare_geojson_collection(results, columns):
    features = []
    count = 0
    geom_idx = next((i for i, c in enumerate(columns)
                     if c in ('geometry', 'st_asgeojson', 'geom', 'way')), None)
    name_idx = next((i for i, c in enumerate(columns) if c == 'name'), None)
    if geom_idx is None:
        return {"type": "FeatureCollection", "features": []}, 0

    for row in results:
        geojson = parse_geojson(row[geom_idx])
        if not geojson:
            continue
        count += 1
        name = row[name_idx] if name_idx is not None else f"Feature {count}"
        props = {c: row[i] for i, c in enumerate(columns)
                 if c not in ('geometry', 'st_asgeojson', 'geom', 'way')
                 and row[i] is not None}
        props.setdefault('name', name or f"Feature {count}")
        features.append({"type": "Feature", "geometry": geojson, "properties": props})

    return {"type": "FeatureCollection", "features": features}, count

def feature_label(sql):
    sql_l = sql.lower()
    patterns = [
        (r"amenity\s*=\s*'(\w+)'",  lambda v: v.replace('_', ' ')),
        (r"leisure\s*=\s*'(\w+)'",  lambda v: v.replace('_', ' ')),
        (r"highway\s*=\s*'(\w+)'",  lambda v: v.replace('_', ' ') + ' path'),
        (r"shop\s*=\s*'(\w+)'",     lambda v: v.replace('_', ' ') + ' shop'),
        (r"tourism\s*=\s*'(\w+)'",  lambda v: v.replace('_', ' ')),
    ]
    for pat, fmt in patterns:
        m = re.search(pat, sql_l)
        if m:
            return fmt(m.group(1))
    if 'edinburgh_deprivation' in sql_l:
        return 'deprivation area'
    return 'result'

def location_label(result):
    loc = result.get('location', '')
    if not loc or loc.lower() in ('edinburgh', 'city centre', ''):
        return 'Edinburgh'
    return loc.title()

def determine_location_phrase(user_query, location, is_city, area_active):
    if area_active:
        return 'within your selected area'

    if is_city or location == 'Edinburgh':
        return 'across Edinburgh'

    q = user_query.lower()
    loc_words = location.lower().split()

    if any(f'near {w}' in q or f'close to {w}' in q for w in loc_words):
        return f'near {location}'

    if any(f'in {w}' in q for w in loc_words):
        return f'in {location}'

    return f'near {location}'

def error_message():
    
    return ("I wasn't able to generate a valid query for that. "
        "Try rephrasing — mention a specific place or activity."
    )

def count_message(row_count, feat, loc_phrase):
    plural = f"{feat}s" if not feat.endswith('s') else feat
    verb = "is" if row_count == 1 else "are"

    return (
        f"There {verb} {row_count} {plural} {loc_phrase}. "
        "Would you like to see where they are, or explore something else?"
    )

def normal_message(row_count, feat, loc_phrase, area_active):
    
    if row_count == 0:
        if area_active:
            return (
                f"I couldn't find any {feat}s within your selected area. "
                "Try clearing the area filter or drawing a larger area."
            )
        return (
            f"I couldn't find any {feat}s matching that query. "
            "Try broadening the area, or ask about a different feature."
        )

    if row_count == 1:
        return (
            f"I found 1 {feat} {loc_phrase}. "
            "Would you like to see it on the map, or explore something nearby?"
        )

    plural = f"{feat}s" if not feat.endswith('s') else feat
    cap = (
        'You can show them on the map, or '
        if row_count <= 1000 else
        'There are quite a few — '
    )

    return (
        f"I found {row_count} {plural} {loc_phrase}. "
        f"{cap}ask a follow-up to narrow things down."
    )



