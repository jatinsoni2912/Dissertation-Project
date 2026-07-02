import re

BASE_RADIUS = {
    'point_dense':   500,   
    'point_medium':  750,   
    'point_large':  1000,   
    'tourism':      1500,   
    'leisure':      1500,   
    'sport':        3000,   
    'default':      1000,   
}

FEATURE_CATEGORY = {
    'cafe':        ('point_dense',  1.0),
    'pub':         ('point_dense',  1.0),
    'bar':         ('point_dense',  1.0),
    'atm':         ('point_dense',  1.0),
    
    'restaurant':  ('point_medium', 1.0),
    'pharmacy':    ('point_medium', 1.0),
    
    'library':     ('point_large',  1.0),
    'post_office': ('point_large',  1.0),
    'supermarket': ('point_large',  1.0),
    
    'hotel':       ('tourism',      2.0),   
    'museum':      ('tourism',      1.0),   
    'attraction':  ('tourism',      1.0),   
    'guest_house': ('tourism',      1.0),   
    
    'park':            ('leisure', 1.0),   
    'nature_reserve':  ('leisure', 2.0),  
    'swimming_pool':   ('leisure', 1.0),   
    'sports_centre':   ('leisure', 1.0),   
    'playground':      ('leisure', 1.0),   
    
    'pitch':           ('sport',   1.0),   
    'golf_course':     ('sport',   2.0),   
}

TERM_TO_FEATURE = {
    'cafe': 'cafe', 'pub': 'pub', 'bar': 'pub',
    'restaurant': 'restaurant', 'eating': 'restaurant',
    'pharmacy': 'pharmacy', 'library': 'library',
    'hotel': 'hotel', 'accommodation': 'hotel',
    'museum': 'museum', 'attraction': 'attraction',
    'supermarket': 'supermarket', 'shopping': 'supermarket',
    'park': 'park', 'dog walking': 'park', 'walking': 'park',
    'football': 'pitch', 'soccer': 'pitch', 'tennis': 'pitch',
    'cricket': 'pitch', 'rugby': 'pitch', 'basketball': 'pitch',
    'bowls': 'pitch', 'hockey': 'pitch',
    'golf': 'golf_course',
    'swimming': 'swimming_pool',
    'cycling': 'pitch',
}

DEFAULT_NEAR_RADIUS = 1000

def get_feature_radius(feature):
    if feature in FEATURE_CATEGORY:
        category, multiplier = FEATURE_CATEGORY[feature]
        return int(BASE_RADIUS[category] * multiplier)
    
    return BASE_RADIUS['default']

def return_explicit_search_radius(user_query, activity_terms):
    q = user_query.lower()

    explicit = re.search(r'\bwithin\s+(\d+(?:\.\d+)?)\s*(metres?|meters?|km|kilometres?|miles?|yards?|yds?)\b', q, re.IGNORECASE)
   
    if explicit:
        value = float(explicit.group(1))
        unit = explicit.group(2).lower()
        
        if unit in ('km', 'kilometre', 'kilometres', 'kilometer', 'kilometers'):
            return int(value * 1000), True
        
        elif unit in ('mile', 'miles'):
            return int(value * 1609), True
        
        elif unit in ('yard', 'yards', 'yd', 'yds'):
            return int(value * 0.9144), True
        
        else:
            return int(value), True

    return DEFAULT_NEAR_RADIUS, False

def extract_location_candidate(user_query):
    within_match = re.search(r'\bwithin\s+\d+\s*(?:metres?|meters?|km|miles?)\s+of\s+(.+?)(?:\?|$)', user_query, re.IGNORECASE)
    
    if within_match:
        return within_match.group(1).strip().strip('?.!,')

    in_match = re.search(r'\b(?:near|in|around|close to|next to)\s+(?:the\s+)?([A-Za-z][a-z]+(?:\s+[A-Za-z][a-z]+){0,2})', user_query, re.IGNORECASE)
    
    if in_match:
        return in_match.group(1).strip()

    return 'Edinburgh'

NEAR_EXPANSION_MULTIPLIERS = [3, 5]

def expand_radius_if_empty(sql, was_explicit, execute_fn):
    if was_explicit:
        return sql, None
    if 'ST_DWITHIN' not in sql.upper():
        return sql, None
    if 'COUNT(' in sql.upper():
        return sql, None
    if 'EDINBURGH_DEPRIVATION' in sql.upper():
        return sql, None

    for multiplier in NEAR_EXPANSION_MULTIPLIERS:
        expanded = re.sub(r'(::geography\s*,\s*)(\d+)(\s*\))',
            lambda m, mul=multiplier: (m.group(1) + str(int(m.group(2)) * mul) + m.group(3)), sql)
        
        result = execute_fn(expanded)
        
        if result.get('success') and len(result.get('results', [])) > 0:
            return expanded, multiplier

    return sql, None




