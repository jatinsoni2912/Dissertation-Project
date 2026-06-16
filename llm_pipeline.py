import ollama
import os
import re
from dotenv import load_dotenv
from database import get_schema, get_ontology_mappings
from prompt import build_prompt
 
load_dotenv()
 
BLOCKED_KEYWORDS = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
                    'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE', 'EXECUTE']

INVALID_TAG_FIXES = {
    "landuse = 'park'":        "leisure = 'park'",
    "landuse='park'":          "leisure = 'park'",
    "amenity = 'post office'": "amenity = 'post_office'",
    "amenity = 'dog_walking'": "leisure = 'park'",
    "amenity = 'dog walking'": "leisure = 'park'",
    "amenity = 'coffee_shop'": "amenity = 'cafe'",
    "amenity = 'supermarket'": "shop = 'supermarket'",
    "highway = 'bike'":        "highway = 'cycleway'",
    "highway = 'bicycle'":     "highway = 'cycleway'",
    "highway = 'walking'":     "highway = 'footway'",
}

SKIP_WORDS = {
    'me', 'the', 'a', 'an', 'some', 'any', 'good', 'nice', 'best',
    'nearest', 'closest', 'find', 'show', 'where', 'can', 'go', 'get',
    'are', 'there', 'parks', 'cafes', 'restaurants', 'cycling', 'walking',
    'swimming', 'running', 'hiking', 'football', 'tennis', 'within',
    'metres', 'kilometers', 'km', 'miles', 'around', 'along', 'want',
    'like', 'need', 'looking', 'place', 'places', 'area', 'edinburgh',
    'city', 'centre',
}

HARDCODED_LOCATIONS = {
    'city centre':   (-3.1883, 55.9533),
    'leith':         (-3.1716, 55.9784),
    'stockbridge':   (-3.2051, 55.9588),
    'morningside':   (-3.2107, 55.9290),
    'portobello':    (-3.1120, 55.9536),
    'bruntsfield':   (-3.2040, 55.9380),
    'newington':     (-3.1809, 55.9365),
    'holyrood':      (-3.1772, 55.9507),
    'princes street':(-3.1936, 55.9521),
    'the meadows':   (-3.1896, 55.9402),
    'ferry road':    (-3.2497, 55.9671),
}

def extract_activity_terms(user_query):
    
    activity_keyword_map = {
        'walking':     'walking',
        'walk':        'walking',
        'cycling':     'cycling',
        'cycle':       'cycling',
        'bike':        'cycling',
        'biking':      'cycling',
        'swimming':    'swimming',
        'swim':        'swimming',
        'running':     'running',
        'run':         'running',
        'jogging':     'jogging',
        'jog':         'jogging',
        'hiking':      'hiking',
        'hike':        'hiking',
        'dog':         'dog walking',
        'dog walking': 'dog walking',
        'relaxing':    'relaxing',
        'relax':       'relaxing',
        'picnic':      'picnic',
        'football':    'football',
        'soccer':      'football',
        'tennis':      'tennis',
        'golf':        'golf',
        'basketball':  'basketball',
        'eating':      'eating',
        'food':        'eating',
        'restaurant':  'eating',
        'drinking':    'drinking',
        'pub':         'drinking',
        'coffee':      'coffee',
        'cafe':        'coffee',
        'shopping':    'shopping',
        'studying':    'studying',
        'library':     'studying',
        'sightseeing': 'sightseeing',
        'museum':      'sightseeing',
        'parking':     'parking',
        'post office': 'post office',
        'healthcare':  'healthcare',
        'hospital':    'healthcare',
    }

    query_lower = user_query.lower()
    found = set()
    for keyword in sorted(activity_keyword_map.keys(), key=len, reverse=True):
        if keyword in query_lower:
            found.add(activity_keyword_map[keyword])
    return list(found)


def extract_location(user_query):
    query_lower = user_query.lower()
    for place, coords in HARDCODED_LOCATIONS.items():
        if place in query_lower:
            return place.title(), coords
    return 'city centre', (-3.1883, 55.9533)

def validate_sql(sql):
    sql_upper = sql.upper().strip()
    for blocked in BLOCKED_KEYWORDS:
        if re.search(r'\b' + blocked + r'\b', sql_upper):
            return False, f"Blocked keyword detected: {blocked}"
    if not sql_upper.startswith('SELECT'):
        return False, "Query must start with SELECT"
    return True, "Valid"

def generate_sql(user_query, model=None):
    if model is None:
        model = os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:1.5b')

    activity_terms = extract_activity_terms(user_query)

    ontology_mappings = get_ontology_mappings(activity_terms) if activity_terms else None

    location_name, (lon, lat) = extract_location(user_query)

    schema = get_schema()

    prompt = build_prompt(user_query, ontology_mappings, schema, location_name, lon, lat)

    response = ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        options={'temperature': 0}
    )

    sql = response['message']['content'].strip()

    is_valid, message = validate_sql(sql)

    return {
        'sql': sql,
        'valid': is_valid,
        'validation_message': message,
        'ontology_used': ontology_mappings is not None,
        'activity_terms_found': activity_terms,
        'location_resolved': location_name,
        'model_used': model
    }