PATTERNS = {
    'count': (
        "Count features city-wide",
        "SELECT COUNT(*) FROM planet_osm_point p WHERE p.amenity = 'post_office';"
    ),
    'city_wide_point': (
        "City-wide point feature — planet_osm_point.\n"
        "  amenity= key: cafes (cafe), pubs (pub), pharmacies (pharmacy), libraries (library), post offices (post_office), restaurants (restaurant), ATMs (atm)\n"
        "  tourism= key: hotels (hotel), museums (museum), attractions (attraction)\n"
        "  shop= key: supermarkets (supermarket)\n"
        "  EXAMPLE: restaurants → WHERE p.amenity = 'restaurant'",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_point p WHERE p.amenity = 'restaurant';"
    ),
    'city_wide_polygon': (
        "City-wide polygon feature — planet_osm_polygon.\n"
        "  leisure= key: parks (park), swimming pools (swimming_pool), golf courses (golf_course), sports centres (sports_centre), nature reserves (nature_reserve), playgrounds (playground)",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p WHERE p.leisure = 'sports_centre';"
    ),
    'city_wide_line': (
        "City-wide CYCLING — planet_osm_line WHERE p.highway = 'cycleway'",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_line p\n"
        "WHERE p.highway = 'cycleway';"
    ),
    'city_wide_walking': (
        "City-wide WALKING or footpaths — planet_osm_line WHERE p.highway IN ('footway','path','pedestrian'). 'path' is a VALUE of p.highway, NOT a separate column",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_line p\n"
        "WHERE p.highway IN ('footway', 'path', 'pedestrian');"
    ),
    'city_wide_running': (
        "City-wide RUNNING or jogging — planet_osm_polygon WHERE p.leisure = 'track'",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p\n"
        "WHERE p.leisure = 'track';"
    ),
    'proximity_point': (
        "Point amenity near {location_name}.\n"
        "  amenity= key: cafes (cafe), pubs (pub), pharmacies (pharmacy), libraries (library), restaurants (restaurant)\n"
        "  shop= key: supermarkets (supermarket)\n"
        "  tourism= key: hotels (hotel), museums (museum), attractions (attraction)",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_point p\n"
        "WHERE p.amenity = 'pub'\n"
        "AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint({lon},{lat}),4326)::geography, {radius});\n"
        "-- For hotels: WHERE p.tourism = 'hotel' AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint({lon},{lat}),4326)::geography, {radius})\n"
        "-- For supermarkets: WHERE p.shop = 'supermarket' AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint({lon},{lat}),4326)::geography, {radius})"
    ),
    'proximity_polygon': (
        "Polygon feature near {location_name} — use planet_osm_polygon for parks/pitches/leisure. Use ST_DWithin NOT ST_Intersects",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p\n"
        "WHERE p.leisure = 'park'\n"
        "AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint({lon},{lat}),4326)::geography, {radius});"
    ),
    'named_area_point': (
        "Point amenity inside named suburb {location_name} — planet_osm_point for cafes/pubs/supermarkets/pharmacies/libraries.\n"
        "  CRITICAL: boundary table MUST be planet_osm_polygon — NEVER planet_osm_point",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_point p\n"
        "JOIN planet_osm_polygon boundary ON ST_Intersects(p.way, boundary.way)\n"
        "WHERE boundary.name ILIKE '%{location_name}%'\n"
        "AND boundary.place IN ('suburb','neighbourhood','quarter','village')\n"
        "AND p.amenity = 'pub';"
    ),
    'named_area_polygon': (
        "Polygon feature inside named suburb {location_name} — planet_osm_polygon for parks/leisure.\n"
        "  CRITICAL: boundary table MUST be planet_osm_polygon — NEVER planet_osm_point",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p\n"
        "JOIN planet_osm_polygon boundary ON ST_Intersects(p.way, boundary.way)\n"
        "WHERE boundary.name ILIKE '%{location_name}%'\n"
        "AND boundary.place IN ('suburb','neighbourhood','quarter','village')\n"
        "AND p.leisure = 'park';"
    ),
    'city_wide_sport': (
        "City-wide sport pitch — planet_osm_polygon with leisure='pitch' AND sport ILIKE '%<sport>%'. No ST_DWithin for city-wide.\n"
        "  football/soccer: (sport ILIKE '%football%' OR sport ILIKE '%soccer%')\n"
        "  all other sports (hockey, basketball, rugby, tennis, cricket, bowls): sport ILIKE '%<sport_name>%'",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p\n"
        "WHERE p.leisure = 'pitch' AND p.sport ILIKE '%hockey%';"
    ),
    'sport_proximity': (
        "Sport pitch near {location_name} — planet_osm_polygon with leisure='pitch' AND sport ILIKE '%<sport>%'.\n"
        "  FOOTBALL MUST USE: (p.sport ILIKE '%football%' OR p.sport ILIKE '%soccer%')\n"
        "  ALL other sports (bowls, hockey, tennis, cricket, rugby, basketball): leisure='pitch' AND sport ILIKE '%<sport_name>%'\n"
        "  CRITICAL: NEVER use leisure='bowls' or leisure='basketball' — always leisure='pitch'",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p\n"
        "WHERE p.leisure = 'pitch'\n"
        "AND (p.sport ILIKE '%football%' OR p.sport ILIKE '%soccer%')\n"
        "AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint({lon},{lat}),4326)::geography, {radius});"
    ),
    'deprivation_only': (
        "Deprivation areas only — no OSM join. Most deprived la_decile<=2, least deprived la_decile>=9",
        "SELECT d.dzname, d.la_decile, ST_AsGeoJSON(d.geom)\n"
        "FROM edinburgh_deprivation d WHERE d.la_decile <= 2 ORDER BY d.la_decile;"
    ),
    'deprivation_cross': (
        "OSM point feature in deprived/least-deprived areas — ALWAYS planet_osm_point cross join.\n"
        "  Covers: cafes (amenity=cafe), pubs (amenity=pub), pharmacies (amenity=pharmacy), restaurants (amenity=restaurant), libraries (amenity=library)\n"
        "  CRITICAL: use ST_Intersects for the JOIN — NOT ST_DWithin. Table is edinburgh_deprivation NOT edin_ind_mult_dep",
        "SELECT p.name, ST_AsGeoJSON(p.way), d.dzname, d.la_decile\n"
        "FROM planet_osm_point p\n"
        "JOIN edinburgh_deprivation d ON ST_Intersects(p.way, d.geom)\n"
        "WHERE p.amenity = 'cafe' AND d.la_decile <= 2;"
    ),
    'deprivation_cross_polygon': (
        "OSM polygon feature in deprived/least-deprived areas — planet_osm_polygon cross join.\n"
        "  Covers: parks (leisure=park), golf courses (leisure=golf_course), sports centres (leisure=sports_centre), nature reserves (leisure=nature_reserve)\n"
        "  CRITICAL: use ST_Intersects for the JOIN. Most deprived=la_decile<=2, least deprived=la_decile>=9",
        "SELECT p.name, ST_AsGeoJSON(p.way), d.dzname, d.la_decile\n"
        "FROM planet_osm_polygon p\n"
        "JOIN edinburgh_deprivation d ON ST_Intersects(p.way, d.geom)\n"
        "WHERE p.leisure = 'golf_course' AND d.la_decile >= 9;"
    ),
    'deprivation_cross_line': (
        "OSM line feature in deprived areas — planet_osm_line cross join.\n"
        "  cycleways: highway='cycleway'\n"
        "  walking/footpaths: highway IN ('footway','path','pedestrian') — 'path' is a VALUE not a column\n"
        "  CRITICAL: use ST_Intersects for the JOIN. Table is edinburgh_deprivation",
        "SELECT p.name, ST_AsGeoJSON(p.way), d.dzname, d.la_decile\n"
        "FROM planet_osm_line p\n"
        "JOIN edinburgh_deprivation d ON ST_Intersects(p.way, d.geom)\n"
        "WHERE p.highway IN ('footway', 'path', 'pedestrian') AND d.la_decile <= 5;"
    ),
    'explicit_limit': (
        "User asks for a specific number of results — add LIMIT",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_point p\n"
        "WHERE p.amenity = 'cafe'\n"
        "AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint({lon},{lat}),4326)::geography, {radius})\n"
        "LIMIT 5;"
    )
}

import re

def get_deprivation_pattern(q):
    """Return deprivation pattern key if query mentions deprivation."""
    is_deprivation = any(w in q for w in ['deprived', 'deprivation', 'decile'])
    if not is_deprivation:
        return None

    is_line_cross = any(w in q for w in ['cycle', 'cycling', 'path', 'walk', 'footway'])
    is_polygon_cross = any(w in q for w in ['park', 'pitch', 'golf', 'swim', 'playground'])
    is_point_cross = bool(re.search(
        r'\b(cafes?|pubs?|bars?|shops?|librar(y|ies)|pharmacies?|restaurants?|schools?|'
        r'hospitals?|doctors?|gp|supermarkets?|hotels?|museums?|churches?|atms?|banks?|post office)\b',
        q
    ))

    if is_line_cross:
        return ['deprivation_cross_line']
    elif is_polygon_cross:
        return ['deprivation_cross_polygon']
    elif is_point_cross:
        return ['deprivation_cross']
    else:
        return ['deprivation_only']


def detect_city_or_proximity_pattern(q, is_city_wide):
    is_running = bool(re.search(r'\b(running|run|jog|jogging)\b', q))
    is_line = bool(re.search(r'\b(cycling|cycle|walking|walk|paths?|footway|biking|bike)\b', q))
    is_polygon = bool(re.search(
        r'\b(parks?|golf|swimming|swim|pitches?|sports?\s+centres?|playground|playgrounds?|'
        r'nature\s+reserves?|sports_centre)\b', q
    ))
    is_point = bool(re.search(
        r'\b(cafes?|pubs?|bars?|pharmacies|pharmacy|librar(y|ies)|restaurants?|supermarkets?|'
        r'shops?|attractions?|tourist|post office)\b', q
    ))

    has_explicit_proximity = bool(re.search(
        r'\b(near|within\s+\d+\s*(metres?|meters?|km|miles?))\b', q
    ))

    if is_city_wide:
        if is_running:
            return ['city_wide_running']
        elif bool(re.search(r'\b(cycling|cycle|bike|biking)\b', q)):
            return ['city_wide_line']
        elif bool(re.search(r'\b(walking|walk|paths?|footway)\b', q)):
            return ['city_wide_walking']
        elif is_line:
            return ['city_wide_line']
        elif is_polygon:
            return ['city_wide_polygon']
        else:
            return ['city_wide_point']

    if has_explicit_proximity:
        if is_line or is_polygon or is_running:
            return ['proximity_polygon']
        else:
            return ['proximity_point']

    if is_running or is_line:
        return ['proximity_polygon', 'named_area_polygon']
    elif is_polygon:
        return ['proximity_polygon', 'named_area_polygon']
    else:
        return ['proximity_point', 'named_area_point']


def select_patterns(user_query, is_city_wide):
    q = user_query.lower()

    if any(w in q for w in ['how many', 'count']):
        return ['count']

    deprivation = get_deprivation_pattern(q)
    if deprivation:
        return deprivation

    if re.search(r'\b(show|find|give)\s+me\s+\d+\b', q):
        return ['explicit_limit']

    is_sport = any(w in q for w in [
        'football', 'soccer', 'tennis', 'cricket', 'rugby', 'pitch',
        'basketball', 'bowls', 'bowling', 'hockey', 'netball',
        'volleyball', 'badminton', 'squash'
    ])
    if is_sport:
        return ['city_wide_sport'] if is_city_wide else ['sport_proximity']

    return detect_city_or_proximity_pattern(q, is_city_wide)


def render_pattern(key, location_name, lon, lat, search_radius=1000):
    label, sql = PATTERNS[key]
    label = label.format(location_name=location_name)
    sql = sql.format(
        location_name=location_name,
        lon=f"{lon:.4f}",
        lat=f"{lat:.4f}",
        radius=search_radius,
    )
    return f"-- {label}\n{sql}"


def build_prompt(user_query, schema, location_name, lon, lat, tag_hints="", is_city_wide=False, search_radius=1000):

    pattern_keys = select_patterns(user_query, is_city_wide)
    patterns_text = "\n\n".join(
        render_pattern(k, location_name, lon, lat, search_radius)
        for k in pattern_keys if k in PATTERNS
    )

    tag_section = (
        f"VERIFIED OSM TAGS (live from database):\n{tag_hints}\n"
        if tag_hints.strip() else ""
    )

    q_lower = user_query.lower()
    has_near = bool(re.search(r'\b(near|within\s+\d+\s*(metres?|meters?|km|miles?))\b', q_lower))

    if is_city_wide:
        location_context = ("LOCATION: City-wide Edinburgh — no ST_DWithin, no boundary JOIN, no LIMIT.")
    
    elif has_near:
        location_context = (
            f"LOCATION: near '{location_name}' (lon={lon:.4f}, lat={lat:.4f}).\n"
            f"USE ST_DWithin with radius {search_radius} metres — do NOT use boundary JOIN or ST_Intersects for proximity.")
    else:
        location_context = (
            f"LOCATION: '{location_name}' suburb (lon={lon:.4f}, lat={lat:.4f}).\n"
            f"For suburb queries use this exact JOIN pattern:\n"
            f"JOIN planet_osm_polygon boundary ON ST_Intersects(p.way, boundary.way)\n"
            f"WHERE boundary.name ILIKE '%{location_name}%'\n"
            f"AND boundary.place IN ('suburb','neighbourhood','quarter','village')\n"
            f"CRITICAL: boundary table is planet_osm_polygon — write it exactly as shown above.")

    return f"""You are a PostGIS SQL expert. Output ONLY raw SQL. No markdown.

SCHEMA:
{schema}

{tag_section}
RULES:
- Alias table as p. Use p.name, p.way, p.amenity, p.leisure, p.highway, p.shop, p.tourism etc.
- Always ST_AsGeoJSON(p.way) — never raw p.way
- NEVER use ST_MakeBox3D — it is not a valid PostGIS function for these queries
- Deprivation: column is geom not way. la_decile<=2 most deprived, >=9 least deprived.
- No deprivation JOIN unless query mentions deprived areas.
- Deprivation table is edinburgh_deprivation
- TAG REFERENCE:
  * libraries → amenity='library'
  * restaurants → amenity='restaurant'
  * supermarkets → shop='supermarket'
  * hotels → tourism='hotel'
  * museums → tourism='museum'
  * tourist attractions → tourism='attraction'
  * swimming pools → leisure='swimming_pool'
  * nature reserves → leisure='nature_reserve'
  * sports centres → leisure='sports_centre'
  * cycleways → highway='cycleway' on planet_osm_line
  * football pitches → leisure='pitch' AND (sport ILIKE '%football%' OR sport ILIKE '%soccer%')
  * all other sport pitches → leisure='pitch' AND sport ILIKE '%<sport>%'
- ALWAYS use ST_SetSRID with ST_MakePoint — NEVER output literal 'lon' or 'lat' in SQL

RELEVANT PATTERN:
{patterns_text}

{location_context}

Q: {user_query}
SQL:"""


def build_tag_section(available_tags):
    if not available_tags:
        return ""
    lines = ["REAL TAG VALUES IN THIS DATABASE — use ONLY these values:"]
    leisure_vals = available_tags.get('leisure_poly', [])
    if leisure_vals:
        quoted = ", ".join(f"'{v}'" for v in leisure_vals[:6])
        lines.append(f"  RULE: {quoted} use leisure= key (NOT amenity=)")
    if available_tags.get('amenity'):
        lines.append(f"  amenity (planet_osm_point): {', '.join(available_tags['amenity'][:20])}")
    if leisure_vals:
        lines.append(f"  leisure (planet_osm_polygon): {', '.join(leisure_vals[:15])}")
    if available_tags.get('highway'):
        lines.append(f"  highway (planet_osm_line): {', '.join(available_tags['highway'][:8])}")
    return "\n".join(lines) + "\n"

def build_location_rule(location_name, lon, lat, is_city_wide, is_named_area, search_radius):
    if is_city_wide:
        return (
            "CRITICAL LOCATION RULE:\n"
            "- This is a CITY-WIDE global search across all of Edinburgh.\n"
            "- DO NOT use ST_DWithin or any coordinate filters.\n"
            "- DO NOT use ST_MakePoint."
        )
    if is_named_area:
        return (
            "CRITICAL LOCATION RULE:\n"
            f"- This query is for the named neighbourhood/area '{location_name}'.\n"
            "- YOU MUST use a spatial JOIN with the boundary polygon (see Examples).\n"
            f"- Filter the boundary table using: boundary.name ILIKE '%{location_name}%'\n"
            "- Do NOT use ST_DWithin or ST_MakePoint."
        )
    return (
        "CRITICAL LOCATION RULE:\n"
        f"- This query is localized near {location_name}.\n"
        f"- YOU MUST use: ST_DWithin(way::geography, ST_MakePoint({lon:.6f},{lat:.6f})::geography, {search_radius})\n"
        f"- Radius is pre-calculated as {search_radius}m — use exactly this value.\n"
        f"- DO NOT add a filter like name = '{location_name}'. The spatial coordinates handle the location perfectly."
    )

def build_prompt(user_query, dynamic_tag_hints, schema, location_name,
                 lon, lat, is_city_wide=False, is_named_area=False,
                 search_radius=1500, examples=None, available_tags=None):

    tag_section = build_tag_section(available_tags)
    location_rule = build_location_rule(location_name, lon, lat, is_city_wide, is_named_area, search_radius)

    return f"""You are a PostGIS expert. Return ONLY valid SQL queries. No text, no markdown.

SCHEMA:
{schema}

{dynamic_tag_hints}
{tag_section}
RULES:
- Output ONLY a raw SELECT query string. Do not use code blocks.
- Always cast geometry using ::geography.
- Count queries must use SELECT COUNT(*) and have NO limit.
- Non-count queries: do NOT add LIMIT — return all results.
- Sports pitches are ALWAYS in planet_osm_polygon with leisure='pitch'. NEVER use planet_osm_line for pitches.
- For specific sports use: AND sport ILIKE '%football%' — sport is a plain text column, NOT an hstore tag.
- Parks, gardens, swimming pools, sports centres are ALWAYS in planet_osm_polygon. NEVER use planet_osm_line for these.
- DEPRIVATION TABLE: edinburgh_deprivation has columns dzname, la_decile, la_rank, geom (EPSG:4326)
- la_decile: 1=most deprived, 10=least deprived
- For deprivation cross-queries JOIN edinburgh_deprivation d ON ST_Intersects(p.way, d.geom)
- Always use d.geom (not d.way) for the deprivation geometry column

{location_rule}

EXAMPLES:
{examples}

NOW GENERATE SQL:
Q: {user_query}
A:"""