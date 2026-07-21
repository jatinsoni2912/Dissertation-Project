import ollama
import os
from dotenv import load_dotenv
from database import get_connection, execute_query
from llm_prompt import build_prompt
from constants import CITY_WIDE_SIGNALS
from location_geocoder import geocode_location
from mcp_utils import return_explicit_search_radius, extract_location_candidate, expand_radius_if_empty
from utils import extract_activity_terms, extract_sql
from llm_client import call_model, default_model

load_dotenv()

def create_baseline_context(user_query, context_location):
    q = user_query.lower()

    is_city_wide = any(sig in q for sig in CITY_WIDE_SIGNALS)
    if not is_city_wide and 'edinburgh' in q and not any(
        ind in q for ind in ['near ', 'in ', 'around ', 'within ']):
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
    search_radius, was_explicit = return_explicit_search_radius(user_query, activity_terms)

    return (location_name, lon, lat, is_city_wide, activity_terms, search_radius, was_explicit)

def generate_sql_baseline(user_query, model, location_name, lon, lat, is_city_wide, search_radius):

    prompt = build_prompt(user_query, location_name, lon, lat, is_city_wide, search_radius)

    try:
        raw_sql = extract_sql(call_model(prompt, model, max_tokens=256))
        llm_error = None

    except RuntimeError as e:
        raw_sql = ''
        llm_error = str(e)
        print(f'[LLM] Call failed: {llm_error}')
        return ''   
    
    return raw_sql

def execute_and_expand_baseline_sql(raw_sql, search_radius, was_explicit):
    if not raw_sql.strip().upper().startswith('SELECT'):
        return raw_sql, {'results': []}, False, 'invalid SQL', []

    db_result = execute_query(raw_sql)
    is_valid = db_result.get('success', False)
    validation_message = 'Valid' if is_valid else db_result.get('error', 'Execution failed')

    fixes = []

    if is_valid and len(db_result.get('results', [])) == 0:
        print(f'[Radius] No results at {search_radius}m — trying expansion...')
        expanded_sql, multiplier = expand_radius_if_empty(raw_sql, was_explicit, execute_query)
        if multiplier:
            expanded_result = execute_query(expanded_sql)
            if expanded_result.get('success'):
                n = len(expanded_result.get('results', []))
                print(f'[Radius] Expanded {multiplier}x ({search_radius}m → {search_radius * multiplier}m) — {n} results found')
                fixes = [f'No results at {search_radius}m — expanded radius {multiplier}x to {search_radius * multiplier}m, found {n} results']
                return expanded_sql, expanded_result, True, 'Valid', fixes
        else:
            print('[Radius] No results even after expansion — area may be genuinely empty')

    return raw_sql, db_result, is_valid, validation_message, fixes

def generate_sql(user_query, model=None, context_location=None):
    if model is None:
        model = default_model()

    location_name, lon, lat, is_city_wide, activity_terms, search_radius, was_explicit = create_baseline_context(user_query, context_location)

    raw_sql = generate_sql_baseline(user_query, model, location_name, lon, lat, is_city_wide, search_radius)

    sql_lower = raw_sql.lower()
    is_dep = 'edinburgh_deprivation' in sql_lower
    
    query_mode = ('deprivation' if (is_dep and 'planet_osm' not in sql_lower)
        else 'cross' if is_dep
        else 'osm')

    final_sql, db_result, is_valid, validation_message, radius_fix = execute_and_expand_baseline_sql(raw_sql, search_radius, was_explicit)

    return {'sql': final_sql, 'valid': is_valid, 'validation_message': validation_message,
        'fixes_applied': radius_fix, 'ontology_used': False, 'activity_terms_found': activity_terms,
        'location_resolved': location_name, 'is_city_wide': is_city_wide, 'model_used': model,
        'query_mode': query_mode, 'approach': 'Approach 1 — LLM Baseline (static schema, no MCP)',
        'mcp_results': db_result.get('results', [])}