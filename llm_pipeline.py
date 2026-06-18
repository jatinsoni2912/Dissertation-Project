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


def generate_sql(user_query, model=None):
    if model is None:
        model = os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:1.5b')

    activity_terms = extract_activity_terms(user_query)

    ontology_mappings = get_ontology_mappings(activity_terms) if activity_terms else None

    location_name, (lon, lat) = extract_location(user_query)

    schema = get_schema()

    prompt = build_prompt(user_query, ontology_mappings, schema, location_name, lon, lat)

    response = ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        options={'temperature': 0}
    )

    sql = response['message']['content'].strip()

    sql, fixes = validate_and_fix(sql)

    is_valid, message = validate_sql(sql)

    return {
        'sql': sql,
        'valid': is_valid,
        'validation_message': message,
        'fixes_applied': fixes,
        'ontology_used': ontology_mappings is not None,
        'activity_terms_found': activity_terms,
        'location_resolved': location_name,
        'model_used': model
    }