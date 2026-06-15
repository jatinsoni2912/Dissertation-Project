import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

def get_schema():
    return """
    TABLE: planet_osm_point (points of interest, shops, amenities)
    COLUMNS: osm_id, name, amenity, leisure, shop, tourism, 
             highway, historic, way (geometry, EPSG:4326)
    
    TABLE: planet_osm_line (roads, paths, rivers)  
    COLUMNS: osm_id, name, highway, leisure, waterway, 
             route, way (geometry, EPSG:4326)
    
    TABLE: planet_osm_polygon (parks, buildings, land use areas)
    COLUMNS: osm_id, name, amenity, leisure, landuse, 
             building, shop, tourism, natural, way (geometry, EPSG:4326)
    
    TABLE: ontology_mappings (activity to OSM tag mappings)
    COLUMNS: id, activity_term, osm_key, osm_value, source, verified
    """    