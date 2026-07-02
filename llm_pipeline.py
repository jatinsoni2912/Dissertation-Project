import ollama
import os
from dotenv import load_dotenv
from database import get_schema, get_connection, get_available_tags, execute_query
from prompt import build_prompt
from constants import CITY_WIDE_SIGNALS
from location_geocoder import geocode_location
from sql_fixer import validate_and_fix
from mcp_utils import resolve_search_radius, extract_location_candidate, expand_radius_if_empty
from utils import extract_activity_terms, extract_sql
from utils import (
    extract_activity_terms,
    extract_location,
    validate_sql,
    get_search_radius,
    get_dynamic_tags_from_db,
    select_examples,
    is_district,
    determine_query_type,
    fix_deprivation_columns,
    check_activity_filter,
    handle_search_fallback,
    adjust_search_radius,
)

load_dotenv()

schema_cache: str = ''

def create_baseline_context(user_query, context_location):
    q = user_query.lower()

    is_city_wide = any(sig in q for sig in CITY_WIDE_SIGNALS)
    if not is_city_wide and 'edinburgh' in q and not any(
        ind in q for ind in ['near ', 'in ', 'around ', 'within ']
    ):
        is_city_wide = True

    location_name = 'Edinburgh'
    lon, lat = -3.1883, 55.9533

    if not is_city_wide:
        candidate = extract_location_candidate(user_query)
        if candidate and candidate.lower() != 'edinburgh':
            conn = get_connection()
            try:
                result = geocode_location(candidate, conn=conn)
                if result:
                    lon, lat, location_name = result
            finally:
                conn.close()

    if context_location is not None:
        location_name, lon, lat = context_location
        is_city_wide = False

    activity_terms = extract_activity_terms(user_query)
    search_radius, was_explicit = resolve_search_radius(user_query, activity_terms)

    return (
        location_name,
        lon,
        lat,
        is_city_wide,
        activity_terms,
        search_radius,
        was_explicit,
    )

def generate_sql_baseline(user_query, model, location_name, lon, lat, is_city_wide, search_radius):
    
    prompt = build_prompt(
        user_query=user_query,
        schema=None,  
        location_name=location_name,
        lon=lon,
        lat=lat,
        is_city_wide=is_city_wide,
        search_radius=search_radius,
    )

    try:
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0, 'num_predict': 256},
        )
        return extract_sql(response['message']['content'].strip())
    
    except Exception:
        return ''
    

def execute_and_expand_baseline_sql(raw_sql, search_radius, was_explicit):
    if not raw_sql.strip().upper().startswith('SELECT'):
        return raw_sql, {'results': []}, False, 'invalid SQL', []

    db_result = execute_query(raw_sql)
    is_valid = db_result.get('success', False)
    validation_message = 'Valid' if is_valid else db_result.get('error', 'Execution failed')

    radius_fix = []

    if is_valid and len(db_result.get('results', [])) == 0:
        expanded_sql, multiplier = expand_radius_if_empty(raw_sql, was_explicit, execute_query)
        if multiplier:
            expanded_result = execute_query(expanded_sql)
            if expanded_result.get('success'):
                return (
                    expanded_sql,
                    expanded_result,
                    True,
                    'Valid',
                    [f'Expanded radius {multiplier}x to {search_radius * multiplier}m']
                )

    return raw_sql, db_result, is_valid, validation_message, radius_fix

def generate_sql(user_query, model, context_location):
    if model is None:
        model = os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:1.5b')

    location_name, lon, lat, is_city_wide, activity_terms, search_radius, was_explicit = create_baseline_context(user_query, context_location)

    raw_sql = generate_sql_baseline(user_query, model, location_name, lon, lat, is_city_wide, search_radius)

    sql_lower = raw_sql.lower()
    is_dep = 'edinburgh_deprivation' in sql_lower
    query_mode = (
        'deprivation' if (is_dep and 'planet_osm' not in sql_lower)
        else 'cross' if is_dep
        else 'osm'
    )

    final_sql, db_result, is_valid, validation_message, radius_fix = execute_and_expand_baseline_sql(raw_sql, search_radius, was_explicit)

    return {
        'sql': final_sql,
        'valid': is_valid,
        'validation_message': validation_message,
        'fixes_applied': radius_fix,
        'ontology_used': False,
        'activity_terms_found': activity_terms,
        'location_resolved': location_name,
        'is_city_wide': is_city_wide,
        'model_used': model,
        'query_mode': query_mode,
        'approach': 'Approach 1 — LLM Baseline (static schema, no MCP)',
        'mcp_results': db_result.get('results', []),
    }