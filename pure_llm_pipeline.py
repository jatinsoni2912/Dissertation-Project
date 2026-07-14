import os
import ollama
from database import execute_query
from utils import extract_sql


def build_schema_context():
    return """
    Table: planet_osm_point (columns: osm_id, name, amenity, shop, tourism, historic, way (geometry))
    Table: planet_osm_polygon (columns: osm_id, name, amenity, building, landuse, leisure, way (geometry))
    Table: planet_osm_line (columns: osm_id, name, highway, way (geometry))
    Table: edinburgh_deprivation (columns: datazone, la_decile, geom (geometry))
    """
def build_static_examples():
    return """
EXAMPLES (Do not copy the coordinates blindly, use your own for the user's location):

User: "Count the post offices"
SQL: SELECT COUNT(*) FROM planet_osm_point p WHERE p.amenity = 'post_office';

User: "Find cafes near Edinburgh Castle"
SQL: SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_point p WHERE p.amenity = 'cafe' AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint(-3.199, 55.948),4326)::geography, 500);

User: "Find parks near Leith"
SQL: SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_polygon p WHERE p.leisure = 'park' AND ST_DWithin(p.way::geography, ST_SetSRID(ST_MakePoint(-3.170, 55.970),4326)::geography, 1500);

User: "Show me all cycle paths in Edinburgh"
SQL: SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_line p WHERE p.highway = 'cycleway';

User: "Show me supermarkets in the most deprived areas"
SQL: SELECT p.name, ST_AsGeoJSON(p.way), d.dzname, d.la_decile FROM planet_osm_point p JOIN edinburgh_deprivation d ON ST_Intersects(p.way, d.geom) WHERE p.shop = 'supermarket' AND d.la_decile <= 2;

User: "Find libraries in Morningside"
SQL: SELECT p.name, ST_AsGeoJSON(p.way) FROM planet_osm_point p JOIN planet_osm_polygon boundary ON ST_Intersects(p.way, boundary.way) WHERE boundary.name ILIKE '%Morningside%' AND boundary.place IN ('suburb','neighbourhood') AND p.amenity = 'library';
    """