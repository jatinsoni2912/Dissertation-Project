import os
import json
import re
import psycopg2
import psycopg2.extras
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from location_geocoder import geocode_location
        

mcp = FastMCP("Edinburgh-PostGIS-Discoverer")
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME', 'geoquery_extended'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '123')
    )

@mcp.tool()
def execute_spatial_query(sql_query):
    
    if any(kw in sql_query.upper() for kw in ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER"]):
        return json.dumps({"success": False, "error": "Write operations blocked."})
        
    conn = None

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql_query)
        if cur.description is None:
            return json.dumps({"success": True, "results": []})
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return json.dumps({"success": True, "query_executed": sql_query, "results": rows}, default=str)
    
    except Exception as e:
        if conn: conn.close()
        return json.dumps({"success": False, "error": str(e)})

@mcp.tool()
def lookup_feature_tags(search_terms):
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        results = []
        
        for term in search_terms:
            cur.execute("SELECT osm_key, osm_value, osm_table FROM ontology_mappings WHERE activity_term ILIKE %s OR osm_value ILIKE %s OR activity_term = %s OR osm_key LIKE %s LIMIT 3;", (f"%{term}%", f"%{term}%", term, f"{term}%"))
            rows = cur.fetchall()
            
            if rows:
                results.append({
                    "query_term": term,
                    "matches": [dict(r) for r in rows]})
        
        cur.close()
        conn.close()
        return json.dumps({"success": True, "results": results}, default=str)
    except Exception as e:
        if conn: conn.close()
        return json.dumps({"success": False, "error": str(e)})
    
    
@mcp.tool()    
def is_query_citywide(query):
    
    CITY_WIDE_SIGNALS = {'in edinburgh', 'across edinburgh', 'throughout edinburgh',
        'all edinburgh', 'edinburgh wide', 'citywide',
        'deprived areas', 'deprived neighbourhoods', 'deprived parts',
        'least deprived', 'most deprived', 'deprivation decile'}
    
    is_citywide = any(sig in query.lower() for sig in CITY_WIDE_SIGNALS)
    if not is_citywide and 'edinburgh' in query.lower() and not any(ind in query.lower() for ind in ['near ', 'in ', 'around ', 'close to ', 'next to ', 'within ']):
        is_citywide = True
        
    return json.dumps({"success": True, "is_citywide": is_citywide})

@mcp.tool()
def geocode_place(location_name):
    try:
        result = geocode_location(location_name)
        if result:
            lon, lat, name = result
            return json.dumps({"success": True, "lon": lon, "lat": lat, "name": name})
        return json.dumps({"success": False, "error": "Location not found"})
    except ImportError:
        return json.dumps({"success": False, "error": "Geocoder unavailable"})

if __name__ == "__main__":
    mcp.run()