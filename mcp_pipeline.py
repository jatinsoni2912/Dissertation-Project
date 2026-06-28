import os
import re
import json
import asyncio
import ollama
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from database import get_ontology_mappings, execute_query

from llm_pipeline import (
    extract_activity_terms,
    extract_location,
    validate_sql
)

from mcp_schema import (
    get_live_schema_via_mcp,
    run_mcp_query_sync,
    start_prewarm,
    resolve_tags_via_mcp,
    check_citywide_via_mcp,
    resolve_location_via_mcp,
)
from mcp_utils import extract_location_candidate, resolve_search_radius, expand_radius_if_empty
from prompt import build_prompt
from utils import extract_activity_terms, extract_sql


load_dotenv()
start_prewarm()

def assemble_context(user_query: str, context_location: tuple):
    is_city_wide = check_citywide_via_mcp(user_query)
    loc_word = 'Edinburgh' if is_city_wide else extract_location_candidate(user_query)
    loc_data = resolve_location_via_mcp(loc_word)

    if context_location:
        name, lon, lat = context_location
        loc_data = {'name': name, 'lon': lon, 'lat': lat}
        is_city_wide = False

    schema, _ = get_live_schema_via_mcp()
    activity_terms = extract_activity_terms(user_query)
    tag_hints = resolve_tags_via_mcp(activity_terms)
    search_radius, was_explicit = resolve_search_radius(user_query, activity_terms)

    return (
        is_city_wide,
        loc_data,
        activity_terms,
        tag_hints,
        schema,
        search_radius,
        was_explicit,
    )


def generate_sql(user_query, model, schema, loc_data, tag_hints, is_city_wide, search_radius):
    prompt = build_prompt(
        user_query=user_query,
        schema=schema,
        location_name=loc_data.get('name', 'Edinburgh'),
        lon=loc_data.get('lon', -3.1883),
        lat=loc_data.get('lat', 55.9533),
        tag_hints=tag_hints,
        is_city_wide=is_city_wide,
        search_radius=search_radius,
    )

    response = ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        options={'temperature': 0, 'num_predict': 512}
    )

    return extract_sql(response['message']['content'].strip())

def execute_and_expand_sql(generated_sql: str, search_radius: int, was_explicit: bool):
    try:
        raw = run_mcp_query_sync(generated_sql)
        data = json.loads(raw.strip())
        is_valid = data.get("success", False)
        validation_message = "Valid" if is_valid else data.get("error", "Execution failed")
        final_sql = data.get("query_executed", generated_sql)
        actual_rows = data.get("results", [])
    
    except Exception as e:
        return generated_sql, [], False, f"MCP execution error: {str(e)}", []

    if is_valid and not was_explicit and len(actual_rows) == 0:
        
        expanded_sql, multiplier = expand_radius_if_empty(final_sql, was_explicit, execute_query)

        if multiplier:
            expanded_result = execute_query(expanded_sql)
            if expanded_result.get('success'):
                
                return (
                    expanded_sql,
                    expanded_result.get('results', []),
                    True,
                    "Valid",
                    [f"Expanded radius {multiplier}x to {search_radius * multiplier}m"]
                )

    return final_sql, actual_rows, is_valid, validation_message, []


MCP_SERVER_HOST = os.getenv('MCP_HOST', 'localhost')
MCP_SERVER_PORT = int(os.getenv('MCP_PORT', '5432'))

DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

async def fetch_schema_from_mcp_server() -> str:
    
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-postgres", DB_URL]
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                schema_query = """
                    SELECT table_name, string_agg(column_name, ', ') as columns
                    FROM information_schema.columns
                    WHERE table_schema = 'public' 
                      AND table_name LIKE 'planet_osm_%'
                    GROUP BY table_name;
                """
                
                result = await session.call_tool("query", {"sql": schema_query})
                
                if result.content and len(result.content) > 0:
                    raw_data = result.content[0].text
                    rows = json.loads(raw_data)
                    
                    schema_lines = [f"TABLE: {row['table_name']} — {row['columns']}" for row in rows]
                    return "\n".join(schema_lines)
                    
    except Exception as e:
        print(f"[MCP] Server failed or timed out: {e}")
        return None


def get_live_schema_via_mcp() -> str:
    
    print("[MCP] Attempting to fetch live schema via npx server...")
    
    live_schema = asyncio.run(fetch_schema_from_mcp_server())
    
    if live_schema:
        print("[MCP] Successfully retrieved live schema.")
        return live_schema

    print("[MCP] Falling back to static schema.")
    return get_static_schema()


def get_static_schema() -> str:
    """Minimal static schema fallback if MCP server is not running."""
    return """
    TABLE: planet_osm_point — amenity, shop, tourism, highway, name, way
    TABLE: planet_osm_line — highway, waterway, route, name, way
    TABLE: planet_osm_polygon — leisure, landuse, amenity, building, name, place, boundary, way
    TABLE: ontology_mappings — activity_term, osm_key, osm_value, verified
    """

MCP_PROMPT = """You are a PostGIS SQL expert generating queries for the Edinburgh geospatial database.
Return ONLY the SQL query — no explanation, no markdown, no text before or after the SQL.

LIVE DATABASE SCHEMA (retrieved via Postgres MCP — use these exact column names):
{live_schema}

{ontology_section}

OSM TAG REFERENCE — use these exact tags:
  Parks and green space  → planet_osm_polygon  WHERE leisure = 'park'
  Gardens                → planet_osm_polygon  WHERE leisure = 'garden'
  Cycleways              → planet_osm_line     WHERE highway = 'cycleway'
  Footways and paths     → planet_osm_line     WHERE highway IN ('footway','path')
  Swimming pools         → planet_osm_polygon  WHERE leisure = 'swimming_pool'
  Sports pitches         → planet_osm_polygon  WHERE leisure = 'pitch'
  Running tracks         → planet_osm_polygon  WHERE leisure IN ('track','sports_centre')
  Golf courses           → planet_osm_polygon  WHERE leisure = 'golf_course'
  Cafes                  → planet_osm_point    WHERE amenity = 'cafe'
  Restaurants            → planet_osm_point    WHERE amenity = 'restaurant'
  Pubs                   → planet_osm_point    WHERE amenity = 'pub'
  Post offices           → planet_osm_point    WHERE amenity = 'post_office'
  Libraries              → planet_osm_point    WHERE amenity = 'library'
  Museums                → planet_osm_point    WHERE tourism = 'museum'
  Parking                → planet_osm_point    WHERE amenity = 'parking'
  Dog walking            → planet_osm_polygon  WHERE leisure = 'park'
  Picnic spots           → planet_osm_polygon  WHERE leisure IN ('park','garden')

RULES:
- Return ONLY the SQL — no explanation text
- Only SELECT statements — never INSERT UPDATE DELETE DROP
- ALWAYS cast: way::geography AND ST_MakePoint(lon,lat)::geography
- NEVER use ST_Intersects for proximity — use ST_DWithin
- In spatial joins ALWAYS use ST_Intersects(p.way, boundary.way) in JOIN ON
- Cycling and hiking: 5000m radius minimum
- Walking: 2000m minimum
- Default radius: 1000m
- Add LIMIT 50 unless counting
- For counts: SELECT COUNT(*) with no LIMIT

DETECTED LOCATION: {location_name} — lon={lon}, lat={lat}

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

USER QUERY: {user_query}

SQL:"""

def generate_sql_with_mcp(user_query: str, model: str = None) -> dict:

    if model is None:
        model = os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:1.5b')

    activity_terms = extract_activity_terms(user_query)
    ontology_mappings = get_ontology_mappings(activity_terms) if activity_terms else None

    location_name, (lon, lat) = extract_location(user_query)

    live_schema = get_live_schema_via_mcp()

    ontology_section = ""
    if ontology_mappings:
        ontology_section = "VERIFIED OSM TAG MAPPINGS:\n"
        for term, mappings in ontology_mappings.items():
            ontology_section += f"  {term}: {', '.join(mappings)}\n"
    else:
        ontology_section = "No ontology mappings found.\n"

    prompt = MCP_PROMPT.format(
        live_schema=live_schema,
        ontology_section=ontology_section,
        location_name=location_name,
        lon=lon,
        lat=lat,
        user_query=user_query,
    )

    response = ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        options={'temperature': 0}
    )

    sql = response['message']['content'].strip()

    is_valid, message = validate_sql(sql)

    return {
        'sql': sql,
        'valid': is_valid,
        'validation_message': message,
        'ontology_used': ontology_mappings is not None,
        'activity_terms_found': activity_terms,
        'location_resolved': location_name,
        'model_used': model,
        'approach': 'Approach 2 — LLM + MCP',
        'schema_source': 'live_mcp' if 'TABLE:' in live_schema else 'static_fallback',
    }