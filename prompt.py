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
    ),
}

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