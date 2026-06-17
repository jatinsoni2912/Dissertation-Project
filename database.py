import psycopg2
import os
from dotenv import load_dotenv
from constants import STREET_SUFFIXES, EXCLUDE_ROUTES_CLAUSE, ORDER_BY_NAME_MATCH

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

def get_ontology_mappings(activity_terms, conn=None):
    is_local_conn = False
    if conn is None:
        conn = get_connection()
        is_local_conn = True
        
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT activity_term, osm_key, osm_value
            FROM ontology_mappings
            WHERE activity_term = ANY(%s)
            AND verified = TRUE
            ORDER BY activity_term, osm_key
        """, (activity_terms,))
        results = cur.fetchall()
    finally:
        cur.close()
        if is_local_conn:
            conn.close()
            
    if not results:
        return None
        
    mappings = {}
    for term, key, value in results:
        if term not in mappings:
            mappings[term] = []
        mappings[term].append(f"{key} = '{value}'")
    return mappings   

def execute_query(sql):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        results = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return {'success': True, 'results': results, 'columns': columns}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        cur.close()
        conn.close()

def is_street_name(location_name):
    words = location_name.lower().strip().split()
    return any(word in STREET_SUFFIXES for word in words)

def find_street_exact(cur, location_name):
    cur.execute(
        "SELECT ST_X(ST_Centroid(way)) AS lon,"
        "       ST_Y(ST_Centroid(way)) AS lat, name"
        " FROM planet_osm_line"
        " WHERE LOWER(name) = LOWER(%s)"
        " AND name IS NOT NULL"
        + EXCLUDE_ROUTES_CLAUSE +
        " LIMIT 1",
        (location_name,)
    )
    return cur.fetchone()

def find_street_word_boundary(cur, location_name):
    cur.execute(
        "SELECT ST_X(ST_Centroid(way)) AS lon,"
        "       ST_Y(ST_Centroid(way)) AS lat, name"
        " FROM planet_osm_line"
        " WHERE name ~* ('\\y' || %s || '\\y')"
        " AND name IS NOT NULL"
        + EXCLUDE_ROUTES_CLAUSE +
        " ORDER BY LENGTH(name) ASC LIMIT 1",
        (location_name,)
    )
    return cur.fetchone()

def find_street_partial(cur, location_name):
    cur.execute(
        "SELECT ST_X(ST_Centroid(way)) AS lon,"
        "       ST_Y(ST_Centroid(way)) AS lat, name"
        " FROM planet_osm_line"
        " WHERE name ILIKE %s AND name IS NOT NULL"
        + EXCLUDE_ROUTES_CLAUSE +
        " ORDER BY (LOWER(name) = LOWER(%s)) DESC,"
        "          LENGTH(name) ASC LIMIT 1",
        (f'%{location_name}%', location_name)
    )
    return cur.fetchone()
