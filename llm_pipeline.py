import ollama
import os
from dotenv import load_dotenv
from database import get_schema, get_connection, get_available_tags
from prompt import build_prompt
from sql_fixer import validate_and_fix
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

def generate_sql(user_query, model=None):
    if model is None:
        model = os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:1.5b')

    activity_terms = extract_activity_terms(user_query)

    conn = get_connection()
    try:
        dynamic_tag_hints = get_dynamic_tags_from_db(user_query, conn)
        location_name, (lon, lat), is_city_wide = extract_location(user_query, conn=conn)

        _explicit_cc = 'city centre' in user_query.lower() or 'city center' in user_query.lower()
        if location_name.lower() == 'city centre' and not is_city_wide and not _explicit_cc:
            is_city_wide = True

        is_named_area = is_district(location_name, conn) if not is_city_wide else False
        available_tags = get_available_tags(conn)
    finally:
        conn.close()

    global schema_cache
    if not schema_cache:
        schema_cache = get_schema()

    search_radius = get_search_radius(activity_terms, user_query)
    examples = select_examples(activity_terms, is_city_wide, is_named_area, user_query)

    prompt = build_prompt(
        user_query, dynamic_tag_hints, schema_cache,
        location_name, lon, lat,
        is_city_wide=is_city_wide,
        is_named_area=is_named_area,
        search_radius=search_radius,
        examples=examples,
        available_tags=available_tags,
    )

    response = ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        options={'temperature': 0},
    )

    sql = response['message']['content'].strip()

    query_mode = determine_query_type(sql)
    is_dep = query_mode in ('deprivation', 'cross')

    sql = check_activity_filter(sql, activity_terms, query_mode, is_city_wide, lon, lat, search_radius)

    if query_mode == 'deprivation':
        sql = fix_deprivation_columns(sql)
        is_valid, message = validate_sql(sql)
        return {
            'sql': sql, 'valid': is_valid, 'validation_message': message, 'fixes_applied': [],
            'ontology_used': bool(dynamic_tag_hints), 'activity_terms_found': activity_terms,
            'location_resolved': location_name, 'is_city_wide': is_city_wide,
            'model_used': model, 'query_mode': 'deprivation', 'approach': 'Approach 1 — LLM only',
        }

    if is_named_area:
        sql, fixes = validate_and_fix(sql, lon=None, lat=None, is_city_wide=False)
    else:
        sql, fixes = validate_and_fix(sql, lon, lat, is_city_wide)

    is_valid, message = validate_sql(sql)

    result = {
        'sql': sql, 'valid': is_valid, 'validation_message': message, 'fixes_applied': fixes,
        'ontology_used': bool(dynamic_tag_hints), 'activity_terms_found': activity_terms,
        'location_resolved': location_name, 'is_city_wide': is_city_wide,
        'model_used': model, 'query_mode': query_mode, 'approach': 'Approach 1 — LLM only',
    }

    if is_valid and is_named_area and 'COUNT(' not in sql.upper():
        result = handle_search_fallback(result, sql, fixes, location_name, lon, lat)

    if is_valid and not is_city_wide and not is_dep and 'COUNT(' not in sql.upper() and 'ST_DWITHIN' in sql.upper():
        result = adjust_search_radius(result, sql, fixes)

    return result