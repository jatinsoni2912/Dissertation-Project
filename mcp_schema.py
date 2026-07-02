import asyncio
import os
import sys
import json
import threading
import re

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MCP_AVAILABLE = True

schema_cache: str = ''
schema_is_live: bool = False

READ_ONLY_GUARD = re.compile(
    r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|GRANT|REVOKE)\b', re.IGNORECASE
)

SERVER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "mcp_server.py")
)

async def call_tool_async(tool_name, arguments):
    server_params = StdioServerParameters(command=sys.executable, args=[SERVER_PATH])
   
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(name=tool_name, arguments=arguments)
            
            if result and getattr(result, "content", None):
                return getattr(result.content[0], "text", "") or "{}"
            
            return json.dumps({"success": False, "error": f"Empty response from {tool_name}."})

def submit_tool_call(tool_name, arguments, timeout=60):
    if not MCP_AVAILABLE:
        return json.dumps({"success": False, "error": "MCP library not installed."})
    
    try:
        return asyncio.run(asyncio.wait_for(call_tool_async(tool_name, arguments), timeout=timeout))
    
    except asyncio.TimeoutError:
        return json.dumps({"success": False, "error": f"Tool call timed out after {timeout}s."})
    
    except Exception as e:
        return json.dumps({"success": False, "error": f"Tool call '{tool_name}' failed: {str(e)}"})


def run_mcp_query_sync(target_sql, timeout=60):
    if READ_ONLY_GUARD.search(target_sql):
        return json.dumps({"success": False, "error": "Write operations blocked."})
    
    return submit_tool_call(
        "execute_spatial_query", {"sql_query": str(target_sql)}, timeout=timeout
    )

def resolve_tags_via_mcp(activity_terms):
    if not MCP_AVAILABLE or not activity_terms:
        return ""

    SKIP_TERMS = {'deprivation', 'dog walking'}
    
    terms = [t for t in activity_terms if t.lower() not in SKIP_TERMS]
    
    if not terms:
        return ""

    raw = submit_tool_call("lookup_feature_tags", {"search_terms": terms}, timeout=15)
    try:
        data = json.loads(raw)
        if not data.get("success") or not data.get("results"):
            return ""
        
        lines = ["VERIFIED OSM TAGS (from live database — use these exact values):"]
        
        for entry in data["results"]:
            term = entry["query_term"]
            matches = entry.get("matches", [])
            if not matches:
                continue
            best = matches[0]
            lines.append(
                f"  - '{term}' → {best['osm_table']}: "
                f"{best['osm_key']} = '{best['osm_value']}'"
            )
            
            for alt in matches[1:]:
                if alt['osm_value'] != best['osm_value']:
                    lines.append(
                        f"    (also: {alt['osm_table']}: "
                        f"{alt['osm_key']} = '{alt['osm_value']}')"
                    )
        return "\n".join(lines) + "\n" if len(lines) > 1 else ""
    
    except Exception:
        return ""
    
def check_citywide_via_mcp(user_query):
    if not MCP_AVAILABLE:
        return False
    raw = submit_tool_call("is_query_citywide", {"query": user_query}, timeout=5)
    
    try:
        return json.loads(raw).get("is_citywide", False)
    
    except Exception:
        return False

def resolve_location_via_mcp(location_name):
    if not MCP_AVAILABLE:
        return {"lon": -3.1883, "lat": 55.9533, "name": "Edinburgh"}
    raw = submit_tool_call("geocode_place", {"location_name": location_name}, timeout=10)
    
    try:
        data = json.loads(raw)
        if data.get("success"):
            return data
    
    except Exception:
        pass
    return {"lon": -3.1883, "lat": 55.9533, "name": "Edinburgh"}

def build_schema_from_mcp_result(raw_result):
    SPATIAL_INSTRUCTIONS = (
        "CRITICAL POSTGIS SPATIAL INSTRUCTIONS:\n"
        "- All coordinates are in WGS84 degrees (SRID 4326).\n"
        "- PROXIMITY (near a location): ALWAYS use ST_DWithin with actual numeric coordinates:\n"
        "  ST_DWithin(way::geography, ST_SetSRID(ST_MakePoint(-3.188267, 55.953251), 4326)::geography, 500)\n"
        "  CRITICAL: NEVER use ST_Intersects for proximity/near queries. NEVER output literal 'lon' or 'lat'.\n"
        "- Deprivation JOIN: use ST_Intersects(p.way, d.geom) — table is edinburgh_deprivation.\n"
        "- edinburgh_deprivation geometry column is 'geom', NOT 'way' and NOT 'geometry'."
    )
    
    SCHEMA_USE_HINTS = {
        "planet_osm_point":      "USE FOR: pubs (amenity=pub), cafes (amenity=cafe), restaurants, libraries, supermarkets (shop=supermarket), pharmacies (amenity=pharmacy), post offices, tourist attractions",
        "planet_osm_polygon":    "USE FOR: parks (leisure=park), pitches (leisure=pitch, sport=...), golf courses, swimming pools, sports centres",
        "planet_osm_line":       "USE FOR: cycleways (highway=cycleway), walking/footpaths (highway=footway OR path)",
        "edinburgh_deprivation": "USE FOR: deprivation queries — geometry column is 'geom' (NOT 'way'). la_decile<=2 = most deprived, la_decile>=9 = least deprived",
    }

    try:
        data = json.loads(raw_result)
        if not data.get("success") or not data.get("results"):
            raise ValueError("empty")
        tables: dict[str, list[str]] = {}
        for row in data["results"]:
            tname = row.get("table_name", "")
            col = f"{row.get('column_name')} ({row.get('data_type')})"
            tables.setdefault(tname, []).append(col)
        lines = ["LIVE DATABASE TABLE SCHEMAS (Dynamically Fetched via MCP):"]
        for i, (tname, cols) in enumerate(tables.items(), 1):
            lines.append(f"\n{i}. {tname}")
            lines.append(f"   Fields: {', '.join(cols)}")
            if tname in SCHEMA_USE_HINTS:
                lines.append(f"   {SCHEMA_USE_HINTS[tname]}")
        lines.append(f"\n{SPATIAL_INSTRUCTIONS}")
        return "\n".join(lines)
    
    except Exception:
        return (
            "LIVE DATABASE TABLE SCHEMAS:\n"
            "1. planet_osm_point   -> Fields: name, amenity, shop, tourism, way (GEOMETRY Point SRID 4326)\n"
            "   USE FOR: pubs (amenity=pub), cafes (amenity=cafe), restaurants (amenity=restaurant), libraries, supermarkets (shop=supermarket), pharmacies, tourist attractions (tourism=attraction)\n"
            "2. planet_osm_polygon -> Fields: name, leisure, landuse, sport, way (GEOMETRY Polygon SRID 4326)\n"
            "   USE FOR: parks (leisure=park), pitches (leisure=pitch, sport=...), golf courses (leisure=golf_course), swimming pools (leisure=swimming_pool), nature reserves (leisure=nature_reserve)\n"
            "3. planet_osm_line    -> Fields: name, highway, route, way (GEOMETRY LineString SRID 4326)\n"
            "   USE FOR: cycleways (highway=cycleway), footpaths (highway=footway OR path)\n"
            "4. edinburgh_deprivation -> Fields: dzname, la_decile, geom (GEOMETRY MultiPolygon SRID 4326)\n"
            "   CRITICAL: geometry column is 'geom' — NOT 'way', NOT 'geometry'. la_decile<=2 most deprived, >=9 least deprived\n\n"
            "PROXIMITY: ST_DWithin(way::geography, ST_SetSRID(ST_MakePoint(lon,lat),4326)::geography, metres)\n"
            "DEPRIVATION JOIN: ST_Intersects(p.way, d.geom) — table edinburgh_deprivation, geom column NOT way"
        )

def get_live_schema_via_mcp():
    global schema_cache, schema_is_live
    
    if schema_is_live and schema_cache:
        return schema_cache, True
    fetch_and_cache_schema()
    
    return schema_cache, schema_is_live

def fetch_and_cache_schema():
    global schema_cache, schema_is_live
    
    schema_query = """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """
    raw = run_mcp_query_sync(schema_query, timeout=30)
    schema_cache = build_schema_from_mcp_result(raw)
    schema_is_live = True

def start_prewarm():
    if MCP_AVAILABLE and not schema_is_live:
        fetch_and_cache_schema()


