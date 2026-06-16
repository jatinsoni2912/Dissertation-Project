def build_prompt(user_query, ontology_mappings, schema, location_name, lon, lat):
    ontology_section = ""
    if ontology_mappings:
        ontology_section = "VERIFIED OSM TAG MAPPINGS FOR THIS QUERY:\n"
        for term, mappings in ontology_mappings.items():
            ontology_section += f"  {term}: {', '.join(mappings)}\n"
        ontology_section += "Use these verified mappings in your SQL query.\n"
    else:
        ontology_section = "No ontology mappings found. Use your knowledge of OSM tags.\n"

    prompt = f"""You are a PostGIS SQL expert generating queries for the Edinburgh geospatial database.

DATABASE SCHEMA:
{schema}

{ontology_section}

STRICT RULES:
- Only generate SELECT statements — never INSERT UPDATE DELETE DROP
- Parks ALWAYS use leisure = 'park' — NEVER landuse = 'park'
- Cycleways ALWAYS use highway = 'cycleway' in planet_osm_line
- Post offices ALWAYS use amenity = 'post_office' with underscore
- Dog walking areas use leisure = 'park' — amenity = 'dog_walking' does NOT exist
- ALWAYS cast both sides: way::geography AND ST_MakePoint(lon,lat)::geography
- NEVER use ST_Intersects for proximity — use ST_DWithin
- Cycling queries use minimum 5000m radius
- Walking queries use minimum 2000m radius
- Default radius 1000m unless specified
- Always include name in SELECT unless counting
- Add LIMIT 50 unless user asks for a count
- For counts use SELECT COUNT(*) with no LIMIT

WHEN USER MENTIONS A NAMED AREA (Leith, Morningside, Portobello etc):
Use a spatial join — do NOT use coordinates for area queries:
SELECT p.name, ST_AsGeoJSON(p.way)
FROM planet_osm_polygon p
JOIN planet_osm_polygon boundary ON ST_Intersects(p.way, boundary.way)
WHERE boundary.name ILIKE '%area_name%'
AND boundary.place IN ('suburb','neighbourhood','quarter','village')
AND p.leisure = 'park'
LIMIT 50;

WHEN NO NAMED AREA — use these resolved coordinates:
Location: {location_name} — lon={lon}, lat={lat}

FEW-SHOT EXAMPLES:

Q: Where can I go cycling in Edinburgh?
A: SELECT name, ST_AsGeoJSON(way) FROM planet_osm_line WHERE highway IN ('cycleway','path') AND ST_DWithin(way::geography, ST_MakePoint(-3.1883, 55.9533)::geography, 5000) LIMIT 50;

Q: Find parks near the city centre
A: SELECT name, ST_AsGeoJSON(way) FROM planet_osm_polygon WHERE leisure = 'park' AND ST_DWithin(way::geography, ST_MakePoint(-3.1883, 55.9533)::geography, 1000) LIMIT 50;

Q: How many post offices are in Edinburgh?
A: SELECT COUNT(*) FROM planet_osm_point WHERE amenity = 'post_office';

Q: Where can I walk my dog near Leith?
A: SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p JOIN planet_osm_polygon boundary ON ST_Intersects(p.way, boundary.way) WHERE boundary.name ILIKE '%leith%' AND boundary.place IN ('suburb','neighbourhood','quarter','village') AND p.leisure = 'park' LIMIT 50;

Q: Find cafes within 500 metres of Princes Street
A: SELECT name, ST_AsGeoJSON(way) FROM planet_osm_point WHERE amenity = 'cafe' AND ST_DWithin(way::geography, ST_MakePoint(-3.1936, 55.9521)::geography, 500) LIMIT 50;

Q: Show me running tracks near Morningside
A: SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p JOIN planet_osm_polygon boundary ON ST_Intersects(p.way, boundary.way) WHERE boundary.name ILIKE '%morningside%' AND boundary.place IN ('suburb','neighbourhood','quarter','village') AND p.leisure = 'track' LIMIT 50;

NOW GENERATE SQL FOR:
Q: {user_query}
A:"""
    
    return prompt