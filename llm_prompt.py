PATTERNS = {
    'count': (
        "Count features city-wide",
        "SELECT COUNT(*) FROM planet_osm_point p WHERE p.amenity = 'post_office';"
    ),
    'city_wide_point': (
        "City-wide point feature — planet_osm_point.\n"
        "  amenity= key: cafes (cafe), pubs (pub), pharmacies (pharmacy), libraries (library),\n"
        "  post offices (post_office), restaurants (restaurant), ATMs (atm)\n"
        "  tourism= key: hotels (hotel), museums (museum), attractions (attraction)\n"
        "  shop= key: supermarkets (supermarket)\n"
        "  EXAMPLE: restaurants → WHERE p.amenity = 'restaurant'",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_point p WHERE p.amenity = 'restaurant';"
    ),
    'city_wide_polygon': (
        "City-wide polygon feature — planet_osm_polygon.\n"
        "  leisure= key: parks (park), swimming pools (swimming_pool), golf courses (golf_course),\n"
        "  sports centres (sports_centre), nature reserves (nature_reserve), playgrounds (playground)",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p WHERE p.leisure = 'sports_centre';"
    ),
    'city_wide_line': (
        "City-wide CYCLING — planet_osm_line WHERE p.highway = 'cycleway'",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_line p\n"
        "WHERE p.highway = 'cycleway';"
    ),
    'city_wide_walking': (
        "City-wide WALKING or footpaths — planet_osm_line WHERE p.highway IN ('footway','path','pedestrian'). 'path' is a VALUE of p.highway",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_line p\n"
        "WHERE p.highway IN ('footway', 'path', 'pedestrian');"
    ),
    'city_wide_running': (
        "City-wide RUNNING or jogging — planet_osm_polygon WHERE p.leisure = 'track'",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p\n"
        "WHERE p.leisure = 'track';"
    ),
    'city_wide_sport': (
        "City-wide sport pitch — planet_osm_polygon with leisure='pitch' AND sport ILIKE '%<sport>%'. No ST_DWithin.\n"
        "  football/soccer: (sport ILIKE '%football%' OR sport ILIKE '%soccer%')\n"
        "  all other sports: leisure='pitch' AND sport ILIKE '%<sport_name>%'",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p\n"
        "WHERE p.leisure = 'pitch' AND p.sport ILIKE '%hockey%';"
    ),
    'proximity_point': (
        "Point amenity near {location_name} — use radius {radius}m.\n"
        "  amenity= key: cafes (cafe), pubs (pub), pharmacies (pharmacy), libraries (library), restaurants (restaurant)\n"
        "  shop= key: supermarkets (supermarket)\n"
        "  tourism= key: hotels (hotel), museums (museum), attractions (attraction)",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_point p\n"
        "WHERE p.amenity = 'pub'\n"
        "AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint({lon},{lat}),4326)::geography, {radius});\n"
        "-- For hotels: WHERE p.tourism = 'hotel' AND ST_DWithin(..., {radius})\n"
        "-- For supermarkets: WHERE p.shop = 'supermarket' AND ST_DWithin(..., {radius})"
    ),
    'proximity_polygon': (
        "Polygon feature near {location_name} — use radius {radius}m. Use ST_DWithin NOT ST_Intersects",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p\n"
        "WHERE p.leisure = 'park'\n"
        "AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint({lon},{lat}),4326)::geography, {radius});"
    ),
    'named_area_point': (
        "Point amenity inside named suburb {location_name} — planet_osm_point.\n"
        "  CRITICAL: boundary table MUST be planet_osm_polygon — NEVER planet_osm_point",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_point p\n"
        "JOIN planet_osm_polygon boundary ON ST_Intersects(p.way, boundary.way)\n"
        "WHERE boundary.name ILIKE '%{location_name}%'\n"
        "AND boundary.place IN ('suburb','neighbourhood','quarter','village')\n"
        "AND p.amenity = 'pub';"
    ),
    'named_area_polygon': (
        "Polygon feature inside named suburb {location_name} — planet_osm_polygon.\n"
        "  CRITICAL: boundary table MUST be planet_osm_polygon — NEVER planet_osm_point",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p\n"
        "JOIN planet_osm_polygon boundary ON ST_Intersects(p.way, boundary.way)\n"
        "WHERE boundary.name ILIKE '%{location_name}%'\n"
        "AND boundary.place IN ('suburb','neighbourhood','quarter','village')\n"
        "AND p.leisure = 'park';"
    ),
    'sport_proximity': (
        "Sport pitch near {location_name} — leisure='pitch' AND sport ILIKE '%<sport>%'. Use radius {radius}m.\n"
        "  FOOTBALL: (sport ILIKE '%football%' OR sport ILIKE '%soccer%')\n"
        "  ALL other sports (bowls, hockey, tennis, cricket, rugby, basketball): sport ILIKE '%<sport_name>%'\n"
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
        "OSM point feature in deprived areas — planet_osm_point cross join.\n"
        "  amenity= key: cafes, pubs, pharmacies, restaurants, libraries\n"
        "  CRITICAL: use ST_Intersects for the JOIN. Table is edinburgh_deprivation",
        "SELECT p.name, ST_AsGeoJSON(p.way), d.dzname, d.la_decile\n"
        "FROM planet_osm_point p\n"
        "JOIN edinburgh_deprivation d ON ST_Intersects(p.way, d.geom)\n"
        "WHERE p.amenity = 'cafe' AND d.la_decile <= 2;"
    ),
    'deprivation_cross_polygon': (
        "OSM polygon feature in deprived areas — planet_osm_polygon cross join.\n"
        "  leisure= key: parks, golf courses, sports centres, nature reserves\n"
        "  Most deprived=la_decile<=2, least deprived=la_decile>=9",
        "SELECT p.name, ST_AsGeoJSON(p.way), d.dzname, d.la_decile\n"
        "FROM planet_osm_polygon p\n"
        "JOIN edinburgh_deprivation d ON ST_Intersects(p.way, d.geom)\n"
        "WHERE p.leisure = 'golf_course' AND d.la_decile >= 9;"
    ),
    'deprivation_cross_line': (
        "OSM line feature in deprived areas — planet_osm_line cross join.\n"
        "  highway IN ('footway','path','pedestrian') for walking — 'path' is a VALUE not a column\n"
        "  CRITICAL: use ST_Intersects for the JOIN. Table is edinburgh_deprivation",
        "SELECT p.name, ST_AsGeoJSON(p.way), d.dzname, d.la_decile\n"
        "FROM planet_osm_line p\n"
        "JOIN edinburgh_deprivation d ON ST_Intersects(p.way, d.geom)\n"
        "WHERE p.highway IN ('footway', 'path', 'pedestrian') AND d.la_decile <= 5;"
    ),
    'explicit_limit': (
        "User asks for a specific number of results near {location_name} — add LIMIT",
        "SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_point p\n"
        "WHERE p.amenity = 'cafe'\n"
        "AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint({lon},{lat}),4326)::geography, {radius})\n"
        "LIMIT {limit};"
    ),
}
