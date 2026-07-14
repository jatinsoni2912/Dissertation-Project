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
