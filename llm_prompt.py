import re
from constants import STATIC_SCHEMA

PATTERNS = {
    'count': ("Count features city-wide",
        "SELECT COUNT(*) FROM planet_osm_point p WHERE p.amenity = 'post_office';"),
    
    'city_wide_point': ("City-wide point feature — planet_osm_point.\n"
        "  amenity= key: cafes (cafe), pubs (pub), pharmacies (pharmacy), libraries (library),\n"
        "  post offices (post_office), restaurants (restaurant), ATMs (atm)\n"
        "  tourism= key: hotels (hotel), museums (museum), attractions (attraction)\n"
        "  shop= key: supermarkets (supermarket)\n"
        "  EXAMPLE: restaurants → WHERE p.amenity = 'restaurant'",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_point p WHERE p.amenity = 'restaurant';"),
    
    'city_wide_polygon': ("City-wide polygon feature — planet_osm_polygon.\n"
        "  leisure= key: parks (park), swimming pools (swimming_pool), golf courses (golf_course),\n"
        "  sports centres (sports_centre), nature reserves (nature_reserve), playgrounds (playground)",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p WHERE p.leisure = 'sports_centre';"),
    
    'city_wide_line': ("City-wide CYCLING — planet_osm_line WHERE p.highway = 'cycleway'",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_line p\n"
        "WHERE p.highway = 'cycleway';"),
    
    'city_wide_walking': ("City-wide WALKING or footpaths — planet_osm_line WHERE p.highway IN ('footway','path','pedestrian'). 'path' is a VALUE of p.highway",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_line p\n"
        "WHERE p.highway IN ('footway', 'path', 'pedestrian');"),
    
    'city_wide_running': ("City-wide RUNNING or jogging — planet_osm_polygon WHERE p.leisure = 'track'",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p\n"
        "WHERE p.leisure = 'track';"),
    
    'city_wide_sport': ("City-wide sport pitch — planet_osm_polygon with leisure='pitch' AND sport ILIKE '%<sport>%'. No ST_DWithin.\n"
        "  football/soccer: (sport ILIKE '%football%' OR sport ILIKE '%soccer%')\n"
        "  all other sports: leisure='pitch' AND sport ILIKE '%<sport_name>%'",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p\n"
        "WHERE p.leisure = 'pitch' AND p.sport ILIKE '%hockey%';"),
    
    'proximity_point': ("Point amenity near {location_name} — use radius {radius}m.\n"
        "  amenity= key: cafes (cafe), pubs (pub), pharmacies (pharmacy), libraries (library), restaurants (restaurant)\n"
        "  shop= key: supermarkets (supermarket)\n"
        "  tourism= key: hotels (hotel), museums (museum), attractions (attraction)",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_point p\n"
        "WHERE p.amenity = 'pub'\n"
        "AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint({lon},{lat}),4326)::geography, {radius});\n"
        "-- For hotels: WHERE p.tourism = 'hotel' AND ST_DWithin(..., {radius})\n"
        "-- For supermarkets: WHERE p.shop = 'supermarket' AND ST_DWithin(..., {radius})"),
    
    'proximity_polygon': ("Polygon feature near {location_name} — use radius {radius}m. Use ST_DWithin NOT ST_Intersects",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p\n"
        "WHERE p.leisure = 'park'\n"
        "AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint({lon},{lat}),4326)::geography, {radius});" ),
    
    'named_area_point': ("Point amenity inside named suburb {location_name} — planet_osm_point.\n"
        "  CRITICAL: boundary table MUST be planet_osm_polygon — NEVER planet_osm_point",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_point p\n"
        "JOIN planet_osm_polygon boundary ON ST_Intersects(p.way, boundary.way)\n"
        "WHERE boundary.name ILIKE '%{location_name}%'\n"
        "AND boundary.place IN ('suburb','neighbourhood','quarter','village')\n"
        "AND p.amenity = 'pub';"),
    
    'named_area_polygon': ("Polygon feature inside named suburb {location_name} — planet_osm_polygon.\n"
        "  CRITICAL: boundary table MUST be planet_osm_polygon — NEVER planet_osm_point",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p\n"
        "JOIN planet_osm_polygon boundary ON ST_Intersects(p.way, boundary.way)\n"
        "WHERE boundary.name ILIKE '%{location_name}%'\n"
        "AND boundary.place IN ('suburb','neighbourhood','quarter','village')\n"
        "AND p.leisure = 'park';"),
    
    'sport_proximity': ("Sport pitch near {location_name} — leisure='pitch' AND sport ILIKE '%<sport>%'. Use radius {radius}m.\n"
        "  FOOTBALL: (sport ILIKE '%football%' OR sport ILIKE '%soccer%')\n"
        "  ALL other sports (bowls, hockey, tennis, cricket, rugby, basketball): sport ILIKE '%<sport_name>%'\n"
        "  CRITICAL: NEVER use leisure='bowls' or leisure='basketball' — always leisure='pitch'",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p\n"
        "WHERE p.leisure = 'pitch'\n"
        "AND (p.sport ILIKE '%football%' OR p.sport ILIKE '%soccer%')\n"
        "AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint({lon},{lat}),4326)::geography, {radius});"),
    
    'deprivation_only': ("Deprivation areas only — no OSM join. Most deprived la_decile<=2, least deprived la_decile>=9",
        "SELECT d.dzname, d.la_decile, ST_AsGeoJSON(d.geom)\n"
        "FROM edinburgh_deprivation d WHERE d.la_decile <= 2 ORDER BY d.la_decile;"),
    
    'deprivation_cross': ("OSM point feature in deprived areas — planet_osm_point cross join.\n"
        "  amenity= key: cafes, pubs, pharmacies, restaurants, libraries\n"
        "  CRITICAL: use ST_Intersects for the JOIN. Table is edinburgh_deprivation",
        "SELECT p.name, ST_AsGeoJSON(p.way), d.dzname, d.la_decile\n"
        "FROM planet_osm_point p\n"
        "JOIN edinburgh_deprivation d ON ST_Intersects(p.way, d.geom)\n"
        "WHERE p.amenity = 'cafe' AND d.la_decile <= 2;"),
    
    'deprivation_cross_polygon': ("OSM polygon feature in deprived areas — planet_osm_polygon cross join.\n"
        "  leisure= key: parks, golf courses, sports centres, nature reserves\n"
        "  Most deprived=la_decile<=2, least deprived=la_decile>=9",
        "SELECT p.name, ST_AsGeoJSON(p.way), d.dzname, d.la_decile\n"
        "FROM planet_osm_polygon p\n"
        "JOIN edinburgh_deprivation d ON ST_Intersects(p.way, d.geom)\n"
        "WHERE p.leisure = 'golf_course' AND d.la_decile >= 9;"),
    
    'deprivation_cross_line': ("OSM line feature in deprived areas — planet_osm_line cross join.\n"
        "  highway IN ('footway','path','pedestrian') for walking — 'path' is a VALUE not a column\n"
        "  CRITICAL: use ST_Intersects for the JOIN. Table is edinburgh_deprivation",
        "SELECT p.name, ST_AsGeoJSON(p.way), d.dzname, d.la_decile\n"
        "FROM planet_osm_line p\n"
        "JOIN edinburgh_deprivation d ON ST_Intersects(p.way, d.geom)\n"
        "WHERE p.highway IN ('footway', 'path', 'pedestrian') AND d.la_decile <= 5;"),
    
    'explicit_limit': ("User asks for a specific number of results near {location_name} — add LIMIT",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_point p\n"
        "WHERE p.amenity = 'cafe'\n"
        "AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint({lon},{lat}),4326)::geography, {radius})\n"
        "LIMIT {limit};")}

def get_deprivation_pattern(q):
    is_deprivation = any(w in q for w in ['deprived', 'deprivation', 'decile'])
    
    if not is_deprivation:
        return None

    is_line_cross = any(w in q for w in ['cycle', 'cycling', 'path', 'walk', 'footway'])
    is_polygon_cross = any(w in q for w in ['park', 'pitch', 'golf', 'swim', 'playground'])

    is_point_cross = bool(re.search(r'\b(cafes?|pubs?|bars?|shops?|librar(y|ies)|pharmacies?|restaurants?|schools?|'
        r'hospitals?|doctors?|gp|supermarkets?|hotels?|museums?|churches?|atms?|banks?|post office)\b',q))

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
    is_line    = bool(re.search(r'\b(cycling|cycle|walking|walk|paths?|footway|biking|bike)\b', q))
    is_polygon = bool(re.search(r'\b(parks?|golf|swimming|swim|pitches?|sports?\s+centres?|'
        r'playground|playgrounds?|nature\s+reserves?)\b', q))
    
    has_proximity = bool(re.search(r'\b(near|within\s+\d+\s*(metres?|meters?|km|miles?|yards?))\b', q))

    if is_city_wide:
        if is_running:
            return ['city_wide_running']
        elif re.search(r'\b(cycling|cycle|bike|biking)\b', q):
            return ['city_wide_line']
        elif re.search(r'\b(walking|walk|paths?|footway)\b', q):
            return ['city_wide_walking']
        elif is_line:
            return ['city_wide_line']
        elif is_polygon:
            return ['city_wide_polygon']
        else:
            return ['city_wide_point']

    else:
        if has_proximity:
            return ['proximity_polygon'] if (is_line or is_polygon or is_running) else ['proximity_point']
        else:
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

    if re.search(r'\b(show|find|give)\s+me\s+(\d+)\b', q):
        return ['explicit_limit']

    is_sport = any(w in q for w in ['football', 'soccer', 'tennis', 'cricket', 'rugby', 'pitch',
        'basketball', 'bowls', 'bowling', 'hockey', 'netball', 'volleyball', 'badminton', 'squash'])
    
    if is_sport:
        return ['city_wide_sport'] if is_city_wide else ['sport_proximity']

    return detect_city_or_proximity_pattern(q, is_city_wide)

def render_pattern(key, location_name, lon, lat, radius, limit = 5):
    
    label, sql = PATTERNS[key]
    label = label.format(location_name=location_name, radius=radius)
    sql = sql.format(location_name=location_name, lon=f"{lon:.4f}", lat=f"{lat:.4f}", radius=radius, limit=limit)
    
    return f"-- {label}\n{sql}"

def build_prompt(user_query, location_name, lon, lat, is_city_wide, search_radius):

    pattern_keys = select_patterns(user_query, is_city_wide)

    limit_match = re.search(r'\b(show|find|give)\s+me\s+(\d+)\b', user_query.lower())
    limit = int(limit_match.group(2)) if limit_match else 5

    patterns_text = "\n\n".join(
        render_pattern(k, location_name, lon, lat, search_radius, limit)
        for k in pattern_keys if k in PATTERNS
    )

    q_lower = user_query.lower()
    has_near = bool(re.search(r'\b(near|within\s+\d+\s*(metres?|meters?|km|miles?|yards?))\b', q_lower))

    if is_city_wide:
        location_context = ("LOCATION: City-wide Edinburgh — no ST_DWithin, no boundary JOIN, no LIMIT.")
    
    elif has_near:
        location_context = (f"LOCATION: near '{location_name}' (lon={lon:.4f}, lat={lat:.4f}).\n"
            f"USE ST_DWithin with radius {search_radius} metres — do NOT use boundary JOIN."
        )
    
    else:
        location_context = (f"LOCATION: '{location_name}' suburb (lon={lon:.4f}, lat={lat:.4f}).\n"
            f"For suburb queries use this exact JOIN pattern:\n"
            f"JOIN planet_osm_polygon boundary ON ST_Intersects(p.way, boundary.way)\n"
            f"WHERE boundary.name ILIKE '%{location_name}%'\n"
            f"AND boundary.place IN ('suburb','neighbourhood','quarter','village')\n"
            f"CRITICAL: boundary table is planet_osm_polygon — write it exactly as shown above.")

    return f"""You are a PostGIS SQL expert. Output ONLY raw SQL. No markdown.

SCHEMA:
{STATIC_SCHEMA}

RULES:
- Alias table as p. Prefix ALL columns: p.name, p.way, p.amenity, p.leisure, p.highway, p.shop, p.tourism
- Always ST_AsGeoJSON(p.way) — never raw p.way
- NEVER use ST_MakeBox3D — it is not a valid PostGIS function for these queries
- Deprivation: column is geom not way. la_decile<=2 most deprived, >=9 least deprived.
- No deprivation JOIN unless query mentions deprived/deprivation/decile.
- Deprivation table is edinburgh_deprivation
- TAG REFERENCE:
  * libraries    → amenity='library'
  * restaurants  → amenity='restaurant'
  * supermarkets → shop='supermarket'
  * hotels       → tourism='hotel'
  * museums      → tourism='museum'
  * attractions  → tourism='attraction'
  * swimming pools  → leisure='swimming_pool'
  * nature reserves → leisure='nature_reserve'
  * sports centres  → leisure='sports_centre'
  * cycleways    → highway='cycleway' on planet_osm_line
  * football     → leisure='pitch' AND (sport ILIKE '%football%' OR sport ILIKE '%soccer%')
  * other sports → leisure='pitch' AND sport ILIKE '%<sport>%'
- ALWAYS ST_SetSRID with ST_MakePoint — NEVER output literal 'lon' or 'lat' in SQL

RELEVANT PATTERN:
{patterns_text}

{location_context}

Q: {user_query}
SQL:"""

