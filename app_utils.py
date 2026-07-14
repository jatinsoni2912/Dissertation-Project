import json
import re
import streamlit as st
from decimal import Decimal

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

def fix_decimal_value(v):
    if isinstance(v, Decimal):
        return int(v) if v == v.to_integral_value() else float(v)
    
    return v

def sanitise_rows(rows):
    return [tuple(fix_decimal_value(v) for v in row) for row in rows]

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
    geom_idx = next((i for i, c in enumerate(columns) if c in ('geometry', 'st_asgeojson', 'geom', 'way')), None)
    name_idx = next((i for i, c in enumerate(columns) if c == 'name'), None)
    
    if geom_idx is None:
        return {"type": "FeatureCollection", "features": []}, 0

    for row in results:
        geojson = parse_geojson(row[geom_idx])
        if not geojson:
            continue
        count += 1
        name = row[name_idx] if name_idx is not None else f"Feature {count}"
        props = {c: fix_decimal_value(row[i]) for i, c in enumerate(columns)
                 if c not in ('geometry', 'st_asgeojson', 'geom', 'way')
                 and row[i] is not None}
        props.setdefault('name', name or f"Feature {count}")
        features.append({"type": "Feature", "geometry": geojson, "properties": props})

    return {"type": "FeatureCollection", "features": features}, count

def feature_label(sql):
    sql_l = sql.lower()
    patterns = [
        (r"amenity\s*=\s*'(\w+)'", lambda v: v.replace('_', ' ')),
        (r"leisure\s*=\s*'(\w+)'",  lambda v: v.replace('_', ' ')),
        (r"highway\s*=\s*'(\w+)'",  lambda v: v.replace('_', ' ') + ' path'),
        (r"shop\s*=\s*'(\w+)'",     lambda v: v.replace('_', ' ') + ' shop'),
        (r"tourism\s*=\s*'(\w+)'",  lambda v: v.replace('_', ' '))
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
        "Try rephrasing — mention a specific place or activity.")

def count_message(row_count, feat, loc_phrase):
    plural = f"{feat}s" if not feat.endswith('s') else feat
    verb = "is" if row_count == 1 else "are"

    return (f"There {verb} {row_count} {plural} {loc_phrase}. "
        "Would you like to see where they are, or explore something else?")

def normal_message(row_count, feat, loc_phrase, area_active):
    
    if row_count == 0:
        if area_active:
            return (f"I couldn't find any {feat}s within your selected area. "
                "Try clearing the area filter or drawing a larger area.")
        
        return (f"I couldn't find any {feat}s matching that query. "
            "Try broadening the area, or ask about a different feature.")

    if row_count == 1:
        return (f"I found 1 {feat} {loc_phrase}. "
            "Would you like to see it on the map, or explore something nearby?")

    plural = f"{feat}s" if not feat.endswith('s') else feat
    cap = ('You can show them on the map, or '
        if row_count <= 1000 else
        'There are quite a few — ')

    return (f"I found {row_count} {plural} {loc_phrase}. "
        f"{cap}ask a follow-up to narrow things down.")

def conversational_response(result, user_query):
    row_count = result.get('row_count', 0)
    is_count = result.get('is_count', False)
    sql = result.get('sql', '')
    feat = feature_label(sql)
    location = location_label(result)
    is_city = result.get('is_city_wide', True)
    area_active = st.session_state.get('area_filter_active', False)

    loc_phrase = determine_location_phrase(user_query=user_query, location=location, is_city=is_city, area_active=area_active)

    if result.get('error'):
        return error_message()

    if is_count:
        return count_message(row_count, feat, loc_phrase)

    return normal_message(row_count, feat, loc_phrase, area_active)

def zero_result_suggestions(sql):
    f = feature_label(sql)
    return [f"Find {f}s in Edinburgh", f"Find {f}s near the city centre", "Show me parks in Edinburgh"]

def count_query_suggestions(sql):
    f = feature_label(sql)
    return [f"Where are the {f}s in Edinburgh?", f"Find {f}s near the city centre", f"Find {f}s in the most deprived areas"]

def category_specific_suggestions(sql, loc, is_city, location):
    if "amenity = 'cafe'" in sql or "amenity='cafe'" in sql:
        return [f"Find pubs near {loc}", f"Find restaurants near {loc}", "Find cafes in the most deprived areas in Edinburgh"]

    if "amenity = 'pub'" in sql or "amenity='pub'" in sql:
        return [f"Find cafes near {loc}", f"Find restaurants near {loc}", f"Find parks near {loc}"]

    if "amenity = 'restaurant'" in sql or "amenity='restaurant'" in sql:
        return [f"Find cafes near {loc}", f"Find pubs near {loc}", "How many restaurants are in Edinburgh?"]

    if "leisure = 'park'" in sql or "leisure='park'" in sql:
        return [f"Find cafes near {loc}", "Where can I go cycling in Edinburgh?" if is_city else f"Find cycle paths near {loc}", "Are there parks in the least deprived areas in Edinburgh?"]

    if "highway = 'cycleway'" in sql or "highway='cycleway'" in sql:
        return ["Where can I go running in Edinburgh?", f"Find parks near {loc}", "Show cycle paths in deprived neighbourhoods"]

    if "leisure = 'pitch'" in sql or "leisure='pitch'" in sql:
        return ["How many sports pitches are there in Edinburgh?", f"Find sports centres near {loc}", "Where can I play tennis near Newington?"]

    if "edinburgh_deprivation" in sql and "planet_osm" not in sql:
        return ["Find cafes in the most deprived areas in Edinburgh", "Show cycle paths in deprived neighbourhoods", "Are there parks in the least deprived areas in Edinburgh?"]

    if "edinburgh_deprivation" in sql:
        return ["Show me the most deprived areas in Edinburgh", "Are there parks in the least deprived areas in Edinburgh?", "Find pubs in the most deprived parts in Edinburgh"]

    if "tourism" in sql:
        return ["Find museums in Edinburgh", f"Find cafes near {loc}","What tourist attractions are there near the Old Town?"]
 
    return [] 

def fallback_suggestions(sql, is_city, location):
    feat = feature_label(sql)

    if is_city:
        return [f"Find {feat}s in Leith", f"Find {feat}s in Stockbridge", "Show me parks in Edinburgh"]

    return [f"Find {feat}s in Edinburgh", f"Find parks near {location}", f"How many {feat}s are in Edinburgh?"]

def apply_area_and_deprivation_rules(s, sql):
    area_active = st.session_state.get('area_filter_active', False)

    if area_active:
        expand = f"Find {feature_label(sql)}s in Edinburgh"
        if expand not in s:
            s = s[:2] + [expand]
        return s

    if 'deprivation' not in ' '.join(s).lower() and 'deprivation' not in sql:
        s.append(f"Find {feature_label(sql)}s in deprived areas of Edinburgh")

    return s

def generate_follow_ups(result, user_query):
    sql = result.get('sql', '').lower()
    row_count = result.get('row_count', 0)
    is_count  = result.get('is_count', False)
    is_city = result.get('is_city_wide', True)
    location = location_label(result)
    loc = location if not is_city else 'Edinburgh'

    if row_count == 0:
        return zero_result_suggestions(sql)

    if is_count:
        return count_query_suggestions(sql)

    s = category_specific_suggestions(sql, loc, is_city, location)

    if not s:
        s = fallback_suggestions(sql, is_city, location)

    s = apply_area_and_deprivation_rules(s, sql)

    return s[:3]





