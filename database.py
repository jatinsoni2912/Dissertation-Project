import psycopg2
import os
from dotenv import load_dotenv
import re

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

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

    TABLE: edinburgh_deprivation (Scottish Index of Multiple Deprivation 2019)
    COLUMNS: ogc_fid, dzname (data zone name), datazone (code),
             la_rank (rank, lower=more deprived),
             la_pct (percentile), la_decile (1=most deprived 10=least deprived),
             geom (geometry, EPSG:4326)
    NOTE: la_decile 1 = most deprived, 10 = least deprived
    CROSS-QUERY PATTERN: JOIN edinburgh_deprivation d ON ST_Intersects(p.way, d.geom)
    """

def detect_table_and_columns(sql):
    if 'edinburgh_deprivation' in sql and 'planet_osm' not in sql:
        return 'edinburgh_deprivation', 'geom', 'dzname'
    
    if 'planet_osm_polygon' in sql:
        return 'planet_osm_polygon', 'way', 'name'
    
    if 'planet_osm_line' in sql:
        return 'planet_osm_line', 'way', 'name'
    
    return 'planet_osm_point', 'way', 'name'

def extract_and_clean_where_clause(sql, table):
    where_m = re.search(r'WHERE\s+(.+?)(?:GROUP\s+BY|ORDER\s+BY|LIMIT|;|$)', sql, re.IGNORECASE | re.DOTALL)
    
    if not where_m:
        return None

    where_clause = where_m.group(1).strip().rstrip(';').strip()

    where_clause = re.sub(r'\b[a-zA-Z]\.', '', where_clause)

    where_clause = re.sub(r'\s*AND\s+ST_Intersects\(\s*way\s*,\s*geom\s*\)', '', where_clause, flags=re.IGNORECASE)

    if table != 'edinburgh_deprivation':
        where_clause = re.sub(r'\s*AND\s+(?:la_decile|dzname|la_rank|la_pct)\s*[^A-Za-z\'"\s][^\n,)]*', '', where_clause, flags=re.IGNORECASE)

    where_clause = re.sub(r'^\s*AND\s+', '', where_clause, flags=re.IGNORECASE).strip()

    return where_clause or None


