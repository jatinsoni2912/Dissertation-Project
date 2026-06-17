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

def find_street(cur, location_name):
    for finder in (find_street_exact, find_street_word_boundary, find_street_partial):
        result = finder(cur, location_name)
        if result:
            return result
    return None

def find_neighbourhood(cur, location_name):
    cur.execute("""
        SELECT ST_X(ST_Centroid(way)) AS lon, ST_Y(ST_Centroid(way)) AS lat, name
        FROM planet_osm_polygon
        WHERE (name ILIKE %s OR name ~* ('\\y' || %s || '\\y'))
        AND place IN ('suburb','neighbourhood','quarter','village','town')
        ORDER BY (LOWER(name) = LOWER(%s)) DESC, (name ~* ('\\y' || %s || '\\y')) DESC, ST_Area(way::geography) DESC
        LIMIT 1
    """, (f'%{location_name}%', location_name, location_name, location_name))
    return cur.fetchone()

def find_polygon_boundary(cur, location_name):
    cur.execute("""
        SELECT ST_X(ST_Centroid(way)) AS lon, ST_Y(ST_Centroid(way)) AS lat, name
        FROM planet_osm_polygon
        WHERE (name ILIKE %s OR name ~* ('\\y' || %s || '\\y')) AND way IS NOT NULL
        ORDER BY (LOWER(name) = LOWER(%s)) DESC, (name ~* ('\\y' || %s || '\\y')) DESC, LENGTH(name) ASC, ST_Area(way::geography) DESC
        LIMIT 1
    """, (f'%{location_name}%', location_name, location_name, location_name))
    return cur.fetchone()

def find_point_of_interest(cur, location_name):
    cur.execute(f"""
        SELECT ST_X(way) AS lon, ST_Y(way) AS lat, name
        FROM planet_osm_point
        WHERE (name ILIKE %s OR name ~* ('\\y' || %s || '\\y'))
        {ORDER_BY_NAME_MATCH} LIMIT 1
    """, (f'%{location_name}%', location_name, location_name, location_name))
    return cur.fetchone()

def find_line_fallback(cur, location_name):
    cur.execute(f"""
        SELECT ST_X(ST_Centroid(way)) AS lon, ST_Y(ST_Centroid(way)) AS lat, name
        FROM planet_osm_line
        WHERE (name ILIKE %s OR name ~* ('\\y' || %s || '\\y')) AND name IS NOT NULL
        {ORDER_BY_NAME_MATCH} LIMIT 1
    """, (f'%{location_name}%', location_name, location_name, location_name))
    return cur.fetchone()


def geocode_location(location_name, conn=None):
    
    is_local_conn = conn is None
    if is_local_conn:
        conn = get_connection()

    cur = conn.cursor()
    try:
        street_like = is_street_name(location_name)

        result = find_street(cur, location_name) if street_like else None
        if not result:
            result = find_neighbourhood(cur, location_name)
        if not result:
            result = find_polygon_boundary(cur, location_name)
        if not result:
            result = find_point_of_interest(cur, location_name)
        if not result and not street_like:
            result = find_line_fallback(cur, location_name)

        return result
    finally:
        cur.close()
        if is_local_conn:
            conn.close()
