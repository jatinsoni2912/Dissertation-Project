import os
import re
import json
import asyncio
import ollama
from dotenv import load_dotenv

from database import execute_query

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

def assemble_context(user_query, context_location):
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

def execute_and_expand_sql(generated_sql, search_radius, was_explicit):
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

def generate_sql_with_mcp(user_query, model=None, context_location=None):
    model = model or os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:1.5b')
    
    is_city_wide, loc_data, activity_terms, tag_hints, schema, search_radius, was_explicit = assemble_context(user_query, context_location)

    generated_sql = generate_sql(user_query, model, schema, loc_data, tag_hints, is_city_wide, search_radius)

    final_sql, actual_rows, is_valid, validation_message, radius_fix = execute_and_expand_sql(generated_sql, search_radius, was_explicit)

    sql_lower = final_sql.lower()
    is_dep = 'edinburgh_deprivation' in sql_lower
    query_mode = (
        'deprivation' if (is_dep and 'planet_osm' not in sql_lower)
        else 'cross' if is_dep
        else 'osm'
    )

    return {
        'sql': final_sql,
        'valid': is_valid,
        'validation_message': validation_message,
        'fixes_applied': radius_fix,
        'ontology_used': True,
        'activity_terms_found': activity_terms,
        'location_resolved': loc_data.get('name', 'Edinburgh'),
        'is_city_wide': is_city_wide,
        'model_used': model,
        'query_mode': query_mode,
        'approach': 'Approach 2 - MCP + LLM SQL Generation',
        'mcp_results': actual_rows,
    }