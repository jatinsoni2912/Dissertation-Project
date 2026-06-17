BLOCKED_KEYWORDS = [
    'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
    'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE', 'EXECUTE',
]

SPORTS = {
    'football', 'soccer', 'cricket', 'tennis', 'rugby',
    'basketball', 'bowls', 'hockey', 'netball', 'volleyball', 'golf',
}

SKIP_WORDS = {
    'me', 'the', 'a', 'an', 'some', 'any', 'good', 'nice', 'best',
    'nearest', 'closest', 'find', 'show', 'where', 'can', 'go', 'get',
    'are', 'there', 'parks', 'cafes', 'restaurants', 'cycling', 'walking',
    'swimming', 'running', 'hiking', 'football', 'tennis', 'within',
    'metres', 'meters', 'kilometers', 'km', 'miles', 'around', 'along',
    'want', 'like', 'need', 'looking', 'place', 'places', 'area',
    'edinburgh', 'city', 'centre', 'near', 'in', 'at', 'of',
    'my', 'dog', 'pub', 'bar', 'cafe', 'shop', 'store',
    'of edinburgh', 'the most', 'the least', 'most deprived', 'least deprived',
    'deprived areas', 'deprived neighbourhoods', 'deprived parts',
}

SKIP_PREFIXES = ('of ', 'the ', 'in the ', 'at the ')

CITY_WIDE_SIGNALS = {
    'in edinburgh', 'across edinburgh', 'throughout edinburgh',
    'all edinburgh', 'edinburgh wide', 'city wide', 'citywide',
    'deprived areas', 'deprived neighbourhoods', 'deprived parts',
    'least deprived', 'most deprived', 'deprivation decile',
}

EXAMPLES = {
    'count':
        "Q: How many post offices are in Edinburgh?\n"
        "A: SELECT COUNT(*) FROM planet_osm_point WHERE amenity='post_office';",

    'city_wide_line':
        "Q: Where can I go cycling in Edinburgh?\n"
        "A: SELECT name, ST_AsGeoJSON(way) FROM planet_osm_line WHERE highway='cycleway';",

    'walking_paths':
        "Q: Find walking paths in Edinburgh\n"
        "A: SELECT name, ST_AsGeoJSON(way) FROM planet_osm_line "
        "WHERE highway IN ('path', 'footway', 'pedestrian');",

    'running':
        "Q: Where can I go running in Edinburgh?\n"
        "A: SELECT name, ST_AsGeoJSON(way) FROM planet_osm_polygon "
        "WHERE leisure IN ('park', 'track', 'nature_reserve');",

    'city_wide_polygon':
        "Q: Where can I go swimming in Edinburgh?\n"
        "A: SELECT name, ST_AsGeoJSON(way) FROM planet_osm_polygon WHERE leisure='swimming_pool';",

    'city_wide_point':
        "Q: What tourist attractions are in Edinburgh?\n"
        "A: SELECT name, ST_AsGeoJSON(way) FROM planet_osm_point WHERE tourism='attraction';",

    'proximity_point':
        "Q: Find cafes within 500 metres of Princes Street\n"
        "A: SELECT name, ST_AsGeoJSON(way) FROM planet_osm_point WHERE amenity='cafe' "
        "AND ST_DWithin(way::geography, ST_MakePoint(-3.1936,55.9521)::geography, 500);",

    'proximity_polygon':
        "Q: Find parks near the city centre\n"
        "A: SELECT name, ST_AsGeoJSON(way) FROM planet_osm_polygon WHERE leisure='park' "
        "AND ST_DWithin(way::geography, ST_MakePoint(-3.1883,55.9533)::geography, 1000);",

    'named_area':
        "Q: Where can I walk my dog near Leith?\n"
        "A: SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p "
        "JOIN planet_osm_polygon boundary ON ST_Intersects(p.way, boundary.way) "
        "WHERE boundary.name ILIKE '%leith%' "
        "AND boundary.place IN ('suburb','neighbourhood','quarter','village') "
        "AND p.leisure = 'park';",

    'sport_proximity':
        "Q: Where can I play cricket near Ferry Road?\n"
        "A: SELECT name, ST_AsGeoJSON(way) FROM planet_osm_polygon "
        "WHERE leisure='pitch' AND sport ILIKE '%cricket%' "
        "AND ST_DWithin(way::geography, ST_MakePoint(-3.2497,55.9671)::geography, 3000);",

    'sport_named_area':
        "Q: Where can I play tennis near Newington?\n"
        "A: SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p "
        "JOIN planet_osm_polygon boundary ON ST_Intersects(p.way, boundary.way) "
        "WHERE boundary.name ILIKE '%newington%' "
        "AND boundary.place IN ('suburb','neighbourhood','quarter','village') "
        "AND p.leisure = 'pitch' AND p.sport ILIKE '%tennis%';",

    'explicit_limit':
        "Q: Show me 5 cafes near the Meadows\n"
        "A: SELECT name, ST_AsGeoJSON(way) FROM planet_osm_point WHERE amenity='cafe' "
        "AND ST_DWithin(way::geography, ST_MakePoint(-3.1896,55.9402)::geography, 1000) LIMIT 5;",

    'deprivation_only':
        "Q: Show me the most deprived areas in Edinburgh\n"
        "A: SELECT dzname, la_decile, la_rank, ST_AsGeoJSON(geom) AS geometry "
        "FROM edinburgh_deprivation WHERE la_decile <= 2 ORDER BY la_decile;",

    'cross_query':
        "Q: Find cafes in the most deprived areas of Edinburgh\n"
        "A: SELECT p.name, ST_AsGeoJSON(p.way) AS geometry, d.dzname, d.la_decile "
        "FROM planet_osm_point p JOIN edinburgh_deprivation d ON ST_Intersects(p.way, d.geom) "
        "WHERE p.amenity = 'cafe' AND d.la_decile <= 2;",
}

ACTIVITY_FEATURE = {
    'cycling':     ('highway', 'cycleway',      'planet_osm_line'),
    'hiking':      ('highway', 'path',          'planet_osm_line'),
    'swimming':    ('leisure', 'swimming_pool', 'planet_osm_polygon'),
    'golf':        ('leisure', 'golf_course',   'planet_osm_polygon'),
    'running':     ('leisure', 'track',         'planet_osm_polygon'),
    'coffee':      ('amenity', 'cafe',          'planet_osm_point'),
    'eating':      ('amenity', 'restaurant',    'planet_osm_point'),
    'drinking':    ('amenity', 'pub',           'planet_osm_point'),
    'studying':    ('amenity', 'library',       'planet_osm_point'),
    'shopping':    ('shop',    'supermarket',   'planet_osm_point'),
    'sightseeing': ('tourism', 'attraction',    'planet_osm_point'),
    'healthcare':  ('amenity', 'hospital',      'planet_osm_point'),
    'parking':     ('amenity', 'parking',       'planet_osm_point'),
}

LANDUSE_CORRECTIONS = {
    'park':              ('leisure', 'park',           'planet_osm_polygon'),
    'recreation_ground': ('leisure', 'park',           'planet_osm_polygon'),
    'pitch':             ('leisure', 'pitch',          'planet_osm_polygon'),
    'garden':            ('leisure', 'garden',         'planet_osm_polygon'),
    'golf_course':       ('leisure', 'golf_course',    'planet_osm_polygon'),
    'swimming_pool':     ('leisure', 'swimming_pool',  'planet_osm_polygon'),
    'sports_centre':     ('leisure', 'sports_centre',  'planet_osm_polygon'),
    'track':             ('leisure', 'track',          'planet_osm_polygon'),
    'nature_reserve':    ('leisure', 'nature_reserve', 'planet_osm_polygon'),
    'playground':        ('leisure', 'playground',     'planet_osm_polygon'),
    'cycleway':          ('highway', 'cycleway',       'planet_osm_line'),
    'footway':           ('highway', 'footway',        'planet_osm_line'),
    'path':              ('highway', 'path',           'planet_osm_line'),
    'cycling':           ('highway', 'cycleway',       'planet_osm_line'),
}

LEISURE_POLYGON_TAGS = [
    'swimming_pool', 'sports_centre', 'golf_course',
    'track', 'garden', 'park', 'nature_reserve', 'playground',
]
