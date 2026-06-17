import re

from database import geocode_location

from constants import (
    BLOCKED_KEYWORDS, SPORTS, SKIP_WORDS, SKIP_PREFIXES,
    CITY_WIDE_SIGNALS, EXAMPLES, ACTIVITY_FEATURE,
    LANDUSE_CORRECTIONS, LEISURE_POLYGON_TAGS,
)

def classify_query(terms, query):
    is_dep = 'deprivation' in terms or any(
        x in query for x in ('deprived', 'deprivation', 'decile', 'affluent')
    )
    return {
        'is_count': any(x in query for x in ('how many', 'count', 'number of')),
        'is_dep':   is_dep,
        'is_cross': is_dep and any(
            x in query for x in
            ('cafe', 'park', 'cycle', 'pub', 'restaurant', 'shop', 'library', 'swim')
        ),
        'has_limit': bool(re.search(r'show me \d+|find \d+|\d+\s+(?:cafes?|parks?|pubs?)', query)),
        'has_sport': any(s in terms for s in SPORTS),
    }


def pick_city_wide_key(terms):
    if 'walking' in terms:     return 'walking_paths'
    if 'running' in terms:     return 'running'
    if any(x in terms for x in ['cycling', 'hiking']):  return 'city_wide_line'
    if any(x in terms for x in ['swimming', 'golf']):   return 'city_wide_polygon'
    return 'city_wide_point'


def pick_example_keys(terms, is_city_wide, is_named_area, flags):
    keys = []
    if flags['is_count']:  keys.append('count')
    if flags['is_cross']:  keys.append('cross_query')
    elif flags['is_dep']:  keys.append('deprivation_only')
    if flags['has_sport']: keys.append('sport_named_area' if is_named_area else 'sport_proximity')
    if flags['has_limit']: keys.append('explicit_limit')

    if is_named_area and not flags['has_sport']:
        keys.append('named_area')
    elif is_city_wide:
        keys.append(pick_city_wide_key(terms))
    elif not flags['is_dep']:
        keys.append(
            'proximity_polygon'
            if any(x in terms for x in ['park', 'swimming', 'golf'])
            else 'proximity_point'
        )
    return keys

def finalise_example_keys(keys):
    seen, chosen = set(), []
    for k in keys:
        if k not in seen and k in EXAMPLES:
            seen.add(k)
            chosen.append(k)
        if len(chosen) == 4:
            break
    if not chosen:
        return ['proximity_point', 'named_area']
    if len(chosen) == 1:
        chosen.append('named_area' if chosen[0] != 'named_area' else 'proximity_point')
    return chosen

def select_examples(activity_terms, is_city_wide, is_named_area, user_query):
    q = user_query.lower()
    terms = [x.lower() for x in (activity_terms or [])]
    flags = classify_query(terms, q)
    keys = pick_example_keys(terms, is_city_wide, is_named_area, flags)
    chosen = finalise_example_keys(keys)
    return '\n\n'.join(EXAMPLES[k] for k in chosen)

def extract_activity_terms(user_query):
    keyword_map = {
        'walking': 'walking',   'walk': 'walking',
        'path': 'walking',      'paths': 'walking',
        'cycling': 'cycling',   'cycle': 'cycling',
        'bike': 'cycling',      'biking': 'cycling',
        'swimming': 'swimming', 'swim': 'swimming',
        'running': 'running',   'run': 'running',
        'hiking': 'hiking',     'hike': 'hiking',
        'dog': 'dog walking',   'dog walking': 'dog walking',
        'park': 'park',         'parks': 'park',
        'relaxing': 'relaxing', 'relax': 'relaxing',
        'picnic': 'picnic',
        'football': 'football', 'soccer': 'football',
        'tennis': 'tennis',     'golf': 'golf',
        'basketball': 'basketball', 'cricket': 'cricket',
        'rugby': 'rugby',       'bowls': 'bowls',
        'bowling': 'bowls',     'hockey': 'hockey',
        'netball': 'netball',   'volleyball': 'volleyball',
        'eating': 'eating',     'food': 'eating',
        'restaurant': 'eating', 'drinking': 'drinking',
        'pub': 'drinking',      'coffee': 'coffee',
        'cafe': 'coffee',       'shopping': 'shopping',
        'studying': 'studying', 'library': 'studying',
        'sightseeing': 'sightseeing', 'museum': 'sightseeing',
        'parking': 'parking',   'post office': 'post office',
        'healthcare': 'healthcare', 'hospital': 'healthcare',
        'deprived': 'deprivation',      'deprivation': 'deprivation',
        'most deprived': 'deprivation', 'least deprived': 'deprivation',
        'poorest': 'deprivation',       'affluent': 'deprivation',
        'poverty': 'deprivation',       'decile': 'deprivation',
        'low income': 'deprivation',    'high income': 'deprivation',
        'inequality': 'deprivation',    'socioeconomic': 'deprivation',
    }
    q = user_query.lower()
    found = set()
    for keyword in sorted(keyword_map.keys(), key=len, reverse=True):
        if keyword in q:
            found.add(keyword_map[keyword])
    return list(found)


def build_location_candidates(query):
    indicators = [
        'near ', 'in ', 'around ', 'at ', 'close to ',
        'next to ', 'towards ', 'along ', 'within ', 'of '
    ]
    candidates = []
    for ind in indicators:
        if ind in query:
            after = query[query.find(ind) + len(ind):].strip()
            words = after.split()
            for length in range(min(4, len(words)), 0, -1):
                candidates.append(' '.join(words[:length]))

    words = query.split()
    for length in range(min(4, len(words)), 0, -1):
        candidates.append(' '.join(words[-length:]))

    return candidates

def candidate_is_valid(candidate):
    if candidate in SKIP_WORDS or len(candidate) < 3:
        return False
    if any(candidate.startswith(p) for p in SKIP_PREFIXES):
        return False
    if candidate.replace('.', '').isdigit():
        return False
    if candidate.split()[0] in ('within', 'metres', 'meters', 'km', 'miles'):
        return False
    return True

def resolve_location(candidates, conn):
    seen = set()
    for candidate in candidates:
        candidate = candidate.strip('?.!, ')
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if not candidate_is_valid(candidate):
            continue
        result = geocode_location(candidate, conn=conn)
        if result:
            lon, lat, matched_name = result
            if len(matched_name) > len(candidate) * 5:
                continue
            print(f"[Geocoder] '{candidate}' -> '{matched_name}' ({lon:.4f}, {lat:.4f})")
            return matched_name, (lon, lat)
    return None

def extract_location(user_query, conn=None):
    q = user_query.lower()

    if any(sig in q for sig in CITY_WIDE_SIGNALS):
        print("[Geocoder] City-wide Edinburgh query detected")
        return 'edinburgh', (-3.1883, 55.9533), True

    has_indicator = any(
        ind in q for ind in ['near ', 'close to ', 'next to ', 'at ', 'around ', 'within ', 'of ']
    )
    if 'edinburgh' in q and not has_indicator:
        print("[Geocoder] Edinburgh mentioned without proximity — city-wide scope")
        return 'edinburgh', (-3.1883, 55.9533), True

    candidates = build_location_candidates(q)
    found = resolve_location(candidates, conn)
    if found:
        name, (lon, lat) = found
        return name, (lon, lat), False

    print("[Geocoder] No location found — defaulting to city centre")
    return 'city centre', (-3.1883, 55.9533), False


def validate_sql(sql):
    sql_upper = sql.upper().strip()
    for keyword in BLOCKED_KEYWORDS:
        if re.search(r'\b' + keyword + r'\b', sql_upper):
            return False, f"Blocked keyword: {keyword}"
    if not sql_upper.startswith('SELECT'):
        return False, "Query must start with SELECT"
    return True, "Valid"


def is_district(location_name, conn):
    if location_name.lower() in ('city centre', 'edinburgh', 'city of edinburgh'):
        return False
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 1 FROM planet_osm_polygon
            WHERE name ILIKE %s
            AND place IN ('suburb','neighbourhood','quarter','village','town')
            LIMIT 1
        """, (f'%{location_name}%',))
        return cur.fetchone() is not None
    finally:
        cur.close()

def get_search_radius(activity_terms, user_query):
    q = user_query.lower()
    terms = [x.lower() for x in activity_terms]
    if 'swimming' in terms or 'swimming' in q:                              
        return 5000
    if any(x in terms for x in ['cycling', 'hiking']) or 'cycleway' in q:  
        return 5000
    if 'golf' in terms or 'golf' in q:                                      
        return 5000
    if any(x in terms for x in ['cricket', 'rugby', 'football', 'tennis', 'basketball']): 
        return 3000
    if 'sports centre' in q or 'sports_centre' in q:                        
        return 3000
    if any(x in terms for x in ['walking', 'dog walking', 'park']) or 'park' in q: 
        return 3000
    
    return 1500

def get_dynamic_tags_from_db(user_query, conn, limit=4):
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT osm_table, osm_key, osm_value, search_term
            FROM osm_feature_map
            ORDER BY search_term <-> %s
            LIMIT %s;
        """, (user_query, limit))
        rows = cur.fetchall()
        if not rows:
            return ""
        hints = "VERIFIED OSM TAG MAPPINGS FOR THIS QUERY:\n"
        for osm_table, osm_key, osm_value, search_term in rows:
            hints += f"  - To find '{search_term}': Use table `{osm_table}` WHERE {osm_key} = '{osm_value}'\n"
        return hints
    except Exception as e:
        print(f"Tag lookup failed: {e}")
        return ""


def determine_query_type(sql):
    is_dep = 'edinburgh_deprivation' in sql.lower()
    if is_dep and 'planet_osm' not in sql.lower():
        return 'deprivation'
    if is_dep:
        return 'cross'
    return 'osm'

def fix_deprivation_columns(sql):
    sql = re.sub(r'\bSELECT\s+name\b', 'SELECT dzname', sql, flags=re.IGNORECASE)
    sql = re.sub(r',\s*name\b(?!\s*\()', ', dzname', sql, flags=re.IGNORECASE)
    sql = re.sub(r'ST_AsGeoJSON\(way\)', 'ST_AsGeoJSON(geom)', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bname\b(?=\s*,|\s+FROM)', 'dzname', sql, flags=re.IGNORECASE)
    return sql

def check_tag_presence(sql, key, val, table, allow_in_clause):
    sql_lower = sql.lower()
    
    if f"{key} = '{val}'" in sql_lower or f"{key}='{val}'" in sql_lower:
        return True
   
    if allow_in_clause and f"'{val}'" in sql_lower and table.lower() in sql_lower:
        return True
    return False

def construct_sql_for_activity_query(table, key, val, is_city_wide, lon, lat, radius):
    base_sql = f"SELECT name, ST_AsGeoJSON(way) AS geometry FROM {table} WHERE {key} = '{val}'"
    
    if is_city_wide:
        return f"{base_sql};"
    
    return (
        f"{base_sql} AND ST_DWithin(way::geography, "
        f"ST_MakePoint({lon:.6f}, {lat:.6f})::geography, {radius});"
    )

def check_activity_filter(sql, activity_terms, query_mode, is_city_wide, lon, lat, radius, allow_in_clause=False):
    if query_mode != 'osm' or not activity_terms:
        return sql

    for term in activity_terms:
        if term not in ACTIVITY_FEATURE:
            continue
            
        exp_key, exp_val, exp_table = ACTIVITY_FEATURE[term]
        
        if not check_tag_presence(sql, exp_key, exp_val, exp_table, allow_in_clause):
            sql = construct_sql_for_activity_query(exp_table, exp_key, exp_val, is_city_wide, lon, lat, radius)
            print(f"[Activity fix] Rebuilt SQL for {term}: {exp_key}='{exp_val}'")
            break
            
    return sql

def extract_tag_parts(where_clause, location_name):
    skip = ('boundary', 'place', 'st_intersects', 'st_dwithin', location_name.lower())
    parts = []
    for part in re.split(r'\s+AND\s+', where_clause, flags=re.IGNORECASE):
        p = part.strip().rstrip(';')
        if not any(x in p.lower() for x in skip):
            parts.append(re.sub(r'^[lp]\.', '', p))
    return parts
