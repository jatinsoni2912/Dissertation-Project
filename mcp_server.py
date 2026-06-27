import os
import json
import re
import psycopg2
import psycopg2.extras
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

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
def execute_spatial_query(sql_query: str) -> str:
    
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
def lookup_feature_tags(search_terms: list[str]) -> str:
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        results = []
        
        for term in search_terms:
            cur.execute("""
                SELECT osm_key, osm_value, osm_table 
                FROM ontology_mappings 
                WHERE activity_term ILIKE %s OR osm_value ILIKE %s OR activity_term = %s OR osm_key LIKE %s
                LIMIT 3;
            """, (f'%{term}%', f'%{term}%', term, f'{term}%'))
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