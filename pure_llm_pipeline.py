import os
import ollama
from database import execute_query
from utils import extract_sql
from llm_client import call_model

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

def build_prompt(user_query):
    schema_context = build_schema_context()
    static_examples = build_static_examples()
    return f"""You are a PostGIS SQL expert. Output ONLY raw SQL. No markdown.

SCHEMA:
{schema_context}

RULES:
- Alias table as p. Use p.name, p.way, p.amenity, p.leisure, p.highway, p.shop, p.tourism etc.
- Always ST_AsGeoJSON(p.way) — never raw p.way
- Deprivation: column is geom not way. la_decile<=2 most deprived, >=9 least deprived.
- No deprivation JOIN unless query mentions deprived areas.
- CORRECT TAGS: swimming_pool NOT swimming | tourism=attraction NOT amenity=tourist_attraction | shop=supermarket NOT amenity=supermarket | football: sport ILIKE '%football%' OR sport ILIKE '%soccer%'
- ALWAYS use ST_SetSRID with ST_MakePoint: ST_SetSRID(ST_MakePoint(lon,lat),4326)::geography
- CRITICAL: You must determine the correct longitude and latitude for Edinburgh locations from your own internal memory. Do not use placeholders.
{static_examples}
Q: {user_query}
SQL:"""

def run_llm(prompt, model):
    try:
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0, 'num_predict': 256},
        )
        return extract_sql(response['message']['content'].strip())
    except Exception:
        return ''

def categorize_sql(raw_sql):
    sql_lower = raw_sql.lower()
    is_dep = 'edinburgh_deprivation' in sql_lower
    if is_dep and 'planet_osm' not in sql_lower:
        return 'deprivation'
    if is_dep:
        return 'cross'
    return 'osm'


def execute_sql(raw_sql):
    db_result = execute_query(raw_sql)
    is_valid = db_result.get('success', False)
    validation_message = 'Valid' if is_valid else db_result.get('error', 'Execution failed')
    return db_result, is_valid, validation_message

def generate_sql_pure_llm(user_query, model):
    model = model or os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:1.5b')
    prompt = build_prompt(user_query)
    raw_sql = run_llm(prompt, model)
    query_mode = categorize_sql(raw_sql)

    if not raw_sql.strip().upper().startswith('SELECT'):
        return {
            'sql': raw_sql,
            'valid': False,
            'validation_message': 'invalid SQL',
            'fixes_applied': [],
            'ontology_used': False,
            'activity_terms_found': [],
            'location_resolved': 'None (Pure LLM Guess)',
            'is_city_wide': False,
            'model_used': model,
            'query_mode': query_mode,
            'approach': 'Approach 0 — Pure LLM (Few-Shot)',
            'mcp_results': [],
        }

    db_result, is_valid, validation_message = execute_sql(raw_sql)

    return {
        'sql': raw_sql,
        'valid': is_valid,
        'validation_message': validation_message,
        'fixes_applied': [],
        'ontology_used': False,
        'activity_terms_found': [],
        'location_resolved': 'None (Pure LLM Guess)',
        'is_city_wide': False,
        'model_used': model,
        'query_mode': query_mode,
        'approach': 'Approach 0 — Pure LLM (Few-Shot)',
        'mcp_results': db_result.get('results', [])}

def generate_sql_pure_llm_using_bedrock(user_query, model):

    try:
        raw_sql = extract_sql(call_model(prompt, model, max_tokens=256))
        
    except Exception as e:
        raw_sql = ''
    
    prompt = build_prompt(user_query)
    query_mode = categorize_sql(raw_sql)

    if not raw_sql.strip().upper().startswith('SELECT'):
        return {
            'sql': raw_sql,
            'valid': False,
            'validation_message': 'invalid SQL',
            'fixes_applied': [],
            'ontology_used': False,
            'activity_terms_found': [],
            'location_resolved': 'None (Pure LLM Guess)',
            'is_city_wide': False,
            'model_used': model,
            'query_mode': query_mode,
            'approach': 'Approach 0 — Pure LLM (Few-Shot)',
            'mcp_results': [],
        }

    db_result, is_valid, validation_message = execute_sql(raw_sql)

    return {
        'sql': raw_sql,
        'valid': is_valid,
        'validation_message': validation_message,
        'fixes_applied': [],
        'ontology_used': False,
        'activity_terms_found': [],
        'location_resolved': 'None (Pure LLM Guess)',
        'is_city_wide': False,
        'model_used': model,
        'query_mode': query_mode,
        'approach': 'Approach 0 — Pure LLM (Few-Shot)',
        'mcp_results': db_result.get('results', [])}