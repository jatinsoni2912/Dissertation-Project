OSM_QUERIES = [
    {"query": "Where can I go cycling in Edinburgh?", "expected_table": "planet_osm_line", "expected_key": "highway", "expected_value": "cycleway", "location_type": "city_wide", "query_type": "features", "category": "city_wide_line"},
    {"query": "Show me parks in Edinburgh", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "park", "location_type": "city_wide", "query_type": "features", "category": "city_wide_polygon"},
    {"query": "Where can I go swimming in Edinburgh?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "swimming_pool", "location_type": "city_wide", "query_type": "features", "category": "city_wide_polygon"},
    {"query": "What tourist attractions are there in Edinburgh?", "expected_table": "planet_osm_point", "expected_key": "tourism", "expected_value": "attraction", "location_type": "city_wide", "query_type": "features", "category": "city_wide_point"},
    {"query": "Find libraries in Edinburgh", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "library", "location_type": "city_wide", "query_type": "features", "category": "city_wide_point"},
    {"query": "Where are the pharmacies in Edinburgh?", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "pharmacy", "location_type": "city_wide", "query_type": "features", "category": "city_wide_point"},
    {"query": "Show me golf courses in Edinburgh", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "golf_course", "location_type": "city_wide", "query_type": "features", "category": "city_wide_polygon"},
    {"query": "Where can I go running in Edinburgh?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "pitch", "location_type": "city_wide", "query_type": "features", "category": "city_wide_polygon"},
    {"query": "Find walking paths in Edinburgh", "expected_table": "planet_osm_line", "expected_key": "highway", "expected_value": "footway", "location_type": "city_wide", "query_type": "features", "category": "city_wide_line"},
    {"query": "How many post offices are in Edinburgh?", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "post_office", "location_type": "city_wide", "query_type": "count", "category": "count"},
    {"query": "How many parks are in Edinburgh?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "park", "location_type": "city_wide", "query_type": "count", "category": "count"},
    {"query": "How many sports pitches are there in Edinburgh?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "pitch", "location_type": "city_wide", "query_type": "count", "category": "count"},
    {"query": "Find cafes within 500 metres of Princes Street", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "cafe", "location_type": "point", "query_type": "features", "category": "proximity_point"},
    {"query": "Find pubs within 300 metres of Princes Street", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "pub", "location_type": "point", "query_type": "features", "category": "proximity_point"},
    {"query": "Find parks near the city centre", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "park", "location_type": "point", "query_type": "features", "category": "proximity_polygon"},
    {"query": "Show me 5 cafes near the Meadows", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "cafe", "location_type": "named_area", "query_type": "features", "category": "proximity_explicit_limit"},
    {"query": "Where can I walk my dog near Leith?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "park", "location_type": "named_area", "query_type": "features", "category": "named_area"},
    {"query": "Find pubs in Stockbridge", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "pub", "location_type": "named_area", "query_type": "features", "category": "named_area"},
    {"query": "Show me parks in Morningside", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "park", "location_type": "named_area", "query_type": "features", "category": "named_area"},
    {"query": "Find supermarkets near Leith", "expected_table": "planet_osm_point", "expected_key": "shop", "expected_value": "supermarket", "location_type": "named_area", "query_type": "features", "category": "named_area"},
    {"query": "Find cafes in Bruntsfield", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "cafe", "location_type": "named_area", "query_type": "features", "category": "named_area"},
    {"query": "Where can I play cricket near Ferry Road?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "pitch", "location_type": "point", "query_type": "features", "category": "sport_proximity"},
    {"query": "Where can I play football near Newington?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "pitch", "location_type": "named_area", "query_type": "features", "category": "sport_named_area"},
    {"query": "Where can I play tennis near Newington?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "pitch", "location_type": "named_area", "query_type": "features", "category": "sport_named_area"},
    {"query": "Where can I play football near Leith?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "pitch", "location_type": "named_area", "query_type": "features", "category": "sport_multi_named_area"}
]

DEPRIVATION_QUERIES = [
    {"query": "Show me the most deprived areas in Edinburgh", "expected_table": "edinburgh_deprivation", "expected_key": "la_decile", "expected_value": "1", "location_type": "city_wide", "query_type": "features", "category": "deprivation_only"},
    {"query": "Show me the least deprived areas in Edinburgh", "expected_table": "edinburgh_deprivation", "expected_key": "la_decile", "expected_value": "10", "location_type": "city_wide", "query_type": "features", "category": "deprivation_only"},
    {"query": "Which areas in Edinburgh are in deprivation decile 1?", "expected_table": "edinburgh_deprivation", "expected_key": "la_decile", "expected_value": "1", "location_type": "city_wide", "query_type": "features", "category": "deprivation_only"},
    {"query": "How many deprived areas are in Edinburgh?", "expected_table": "edinburgh_deprivation", "expected_key": "la_decile", "expected_value": "2", "location_type": "city_wide", "query_type": "count", "category": "deprivation_count"},
    {"query": "Find cafes in the most deprived areas in Edinburgh", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "cafe", "location_type": "city_wide", "query_type": "features", "category": "cross_query"},
    {"query": "Show cycle paths in deprived neighbourhoods", "expected_table": "planet_osm_line", "expected_key": "highway", "expected_value": "cycleway", "location_type": "city_wide", "query_type": "features", "category": "cross_query"},
    {"query": "Are there parks in the least deprived areas in Edinburgh?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "park", "location_type": "city_wide", "query_type": "features", "category": "cross_query"},
    {"query": "Find pubs in the most deprived parts in Edinburgh", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "pub", "location_type": "city_wide", "query_type": "features", "category": "cross_query"}
]

EXTENDED_OSM_QUERIES = [
    {"query": "Where can I play basketball in Edinburgh?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "pitch", "location_type": "city_wide", "query_type": "features", "category": "sport_city_wide"},
    {"query": "Find bowls clubs near Morningside", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "pitch", "location_type": "named_area", "query_type": "features", "category": "sport_named_area"},
    {"query": "Where can I play hockey in Edinburgh?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "pitch", "location_type": "city_wide", "query_type": "features", "category": "sport_city_wide"},
    {"query": "Where can I play rugby near Leith?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "pitch", "location_type": "named_area", "query_type": "features", "category": "sport_named_area"},
    {"query": "Where are Edinburgh's playgrounds?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "playground", "location_type": "city_wide", "query_type": "features", "category": "city_wide_polygon"},
    {"query": "Show me nature reserves in Edinburgh", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "nature_reserve", "location_type": "city_wide", "query_type": "features", "category": "city_wide_polygon"},
    {"query": "Find sports centres in Edinburgh", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "sports_centre", "location_type": "city_wide", "query_type": "features", "category": "city_wide_polygon"},
    {"query": "Find restaurants in Edinburgh", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "restaurant", "location_type": "city_wide", "query_type": "features", "category": "city_wide_point"},
    {"query": "Show me hotels near the Royal Mile", "expected_table": "planet_osm_point", "expected_key": "tourism", "expected_value": "hotel", "location_type": "point", "query_type": "features", "category": "proximity_point"},
    {"query": "Find museums in Edinburgh", "expected_table": "planet_osm_point", "expected_key": "tourism", "expected_value": "museum", "location_type": "city_wide", "query_type": "features", "category": "city_wide_point"},
    {"query": "Where are the ATMs in Edinburgh?", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "atm", "location_type": "city_wide", "query_type": "features", "category": "city_wide_point"},
    {"query": "Find restaurants near Stockbridge", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "restaurant", "location_type": "named_area", "query_type": "features", "category": "named_area"},
    {"query": "How many cafes are in Edinburgh?", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "cafe", "location_type": "city_wide", "query_type": "count", "category": "count"},
    {"query": "How many pubs are in Edinburgh?", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "pub", "location_type": "city_wide", "query_type": "count", "category": "count"}
]

DEPRIVATION_QUERIES = [
    {"query": "Show me the most deprived areas in Edinburgh", "expected_table": "edinburgh_deprivation", "expected_key": "la_decile", "expected_value": "1", "location_type": "city_wide", "query_type": "features", "category": "deprivation_only"},
    {"query": "Show me the least deprived areas in Edinburgh", "expected_table": "edinburgh_deprivation", "expected_key": "la_decile", "expected_value": "10", "location_type": "city_wide", "query_type": "features", "category": "deprivation_only"},
    {"query": "Which areas in Edinburgh are in deprivation decile 1?", "expected_table": "edinburgh_deprivation", "expected_key": "la_decile", "expected_value": "1", "location_type": "city_wide", "query_type": "features", "category": "deprivation_only"},
    {"query": "How many deprived areas are in Edinburgh?", "expected_table": "edinburgh_deprivation", "expected_key": "la_decile", "expected_value": "2", "location_type": "city_wide", "query_type": "count", "category": "deprivation_count"},
    {"query": "Find cafes in the most deprived areas in Edinburgh", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "cafe", "location_type": "city_wide", "query_type": "features", "category": "cross_query"},
    {"query": "Show cycle paths in deprived neighbourhoods", "expected_table": "planet_osm_line", "expected_key": "highway", "expected_value": "cycleway", "location_type": "city_wide", "query_type": "features", "category": "cross_query"},
    {"query": "Are there parks in the least deprived areas in Edinburgh?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "park", "location_type": "city_wide", "query_type": "features", "category": "cross_query"},
    {"query": "Find pubs in the most deprived parts in Edinburgh", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "pub", "location_type": "city_wide", "query_type": "features", "category": "cross_query"}
]

EXTENDED_DEPRIVATION_QUERIES = [
    {"query": "Find restaurants in the most deprived areas in Edinburgh", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "restaurant", "location_type": "city_wide", "query_type": "features", "category": "cross_query"},
    {"query": "Find pharmacies in deprived areas of Edinburgh", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "pharmacy", "location_type": "city_wide", "query_type": "features", "category": "cross_query"},
    {"query": "Show walking paths in deprived neighbourhoods", "expected_table": "planet_osm_line", "expected_key": "highway", "expected_value": "footway", "location_type": "city_wide", "query_type": "features", "category": "cross_query"},
    {"query": "Find golf courses in the least deprived areas", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "golf_course", "location_type": "city_wide", "query_type": "features", "category": "cross_query"},
    {"query": "How many parks are in deprived areas of Edinburgh?", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "park", "location_type": "city_wide", "query_type": "count", "category": "cross_query_count"}
]

EXPLICIT_DISTANCE_QUERIES = [
    {"query": "Find pubs within 300 metres of Holyrood Road", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "pub", "location_type": "point", "query_type": "features", "category": "explicit_distance"},
    {"query": "Show me parks within 2 km of the city centre", "expected_table": "planet_osm_polygon", "expected_key": "leisure", "expected_value": "park", "location_type": "point", "query_type": "features", "category": "explicit_distance"},
    {"query": "Find restaurants within 1 km of Waverley Station", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "restaurant", "location_type": "point", "query_type": "features", "category": "explicit_distance"}
]

LANDMARK_PROXIMITY_QUERIES = [
    {"query": "Find cafes near Edinburgh Castle", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "cafe", "location_type": "point", "query_type": "features", "category": "landmark_proximity"},
    {"query": "Find pubs near Waverley Station", "expected_table": "planet_osm_point", "expected_key": "amenity", "expected_value": "pub", "location_type": "point", "query_type": "features", "category": "landmark_proximity"}
]



