import json
import re
import streamlit as st

from database import execute_query, get_feature_locations_for_count
from app_utils import prepare_geojson_collection, sanitise_rows
from mcp_pipeline import generate_sql_with_mcp
from llm_pipeline import generate_sql
        

def apply_area_filter(sql):
    if not (st.session_state.area_filter_active
            and st.session_state.get('area_filter_geojson')):
        return sql

    gj = json.dumps(st.session_state.area_filter_geojson)
    sql_l = sql.lower()

    gcol = 'd.geom' if ('edinburgh_deprivation' in sql_l and 'planet_osm' not in sql_l) else 'p.way'
    cond = (f"ST_Intersects({gcol}::geometry, "
            f"ST_SetSRID(ST_GeomFromGeoJSON('{gj}'), 4326))")

    if 'join planet_osm_polygon boundary' in sql_l:
        sql = re.sub(r'(?i)\s*JOIN\s+planet_osm_polygon\s+boundary\s+ON\s+ST_Intersects\([^)]+\)', '', sql)
        sql = re.sub(r'(?i)(WHERE|AND)\s+boundary\.name\s+ILIKE\s+\S+\s*', lambda m: m.group(1) + ' ', sql)
        sql = re.sub(r'(?i)\s*AND\s+boundary\.place\s+IN\s+\([^)]+\)', '', sql)
        sql = re.sub(r'(?i)WHERE\s+AND\s+', 'WHERE ', sql)
        
        return sql.rstrip(';') + f' AND {cond};'

    if 'WHERE' in sql.upper():
        patched = re.sub(r'(?i)(\bORDER BY\b|\bLIMIT\b|;)', f'AND {cond} \\1', sql, count=1)
        
        return patched if cond in patched else sql.rstrip(';') + f' AND {cond};'

    return sql.rstrip(';') + f' WHERE {cond};'

def generate_sql_result(pipeline_query, model_choice, approach_choice, context_loc):
    
    if "MCP" in approach_choice:
        gen_result = generate_sql_with_mcp(pipeline_query, model=model_choice, context_location=context_loc)
        label = "LLM + MCP"
    else:
        gen_result = generate_sql(pipeline_query, model=model_choice, context_location=context_loc)
        label = "LLM only"

    return gen_result, label

def build_base_metadata(gen_result, approach_label, model_choice):
    
    return {
        "sql": gen_result["sql"],
        "ontology_used": gen_result.get("ontology_used", False),
        "activity_terms": gen_result.get("activity_terms_found", []),
        "location": gen_result.get("location_resolved", ""),
        "approach": approach_label,
        "fixes": gen_result.get("fixes_applied", []),
        "is_city_wide": gen_result.get("is_city_wide", True),
        "classification": gen_result.get("classification"),
        "model_used": model_choice,
    }

def handle_invalid_sql(base, gen_result):
    return {**base, "row_count": 0, "is_count": False, "error": gen_result["validation_message"], "geojson_data": {"type": "FeatureCollection", "features": []}}

def handle_db_error(base, db_result):
    return {**base, "row_count": 0, "is_count": False, "error": db_result["error"], "geojson_data": {"type": "FeatureCollection", "features": []}}

def is_count_query(columns):
    if not columns:
        return False
    col = columns[0].lower()
    return col in ("count", "total", "count_big") or "count" in col

def handle_count_query(base, sql, results, columns):
    count_value = results[0][0] if results else 0

    loc_rows = get_feature_locations_for_count(sql)
    if loc_rows:
        geojson, _ = prepare_geojson_collection(loc_rows, ["name", "geometry"])
    else:
        geojson = {"type": "FeatureCollection", "features": []}
    
    safe_results = sanitise_rows(results)

    return {**base, "row_count": count_value, "is_count": True, "count_value": count_value, "results": safe_results, "columns": columns, "geojson_data": geojson}

def handle_feature_query(base, results, columns):
    geojson, feature_count = prepare_geojson_collection(results, columns)
    safe_results = sanitise_rows(results)
    
    return {**base, "row_count": feature_count, "is_count": False, "results": safe_results, "columns": columns, "geojson_data": geojson}

def handle_results(base, sql, db_result):
    results = db_result["results"]
    columns = db_result["columns"]

    if is_count_query(columns):
        return handle_count_query(base, sql, results, columns)

    return handle_feature_query(base, results, columns)

def run_query(user_query, model_choice, approach_choice, context_loc, pipeline_query):
    
    gen_result, approach_label = generate_sql_result(pipeline_query, model_choice, approach_choice, context_loc)
    base = build_base_metadata(gen_result, approach_label, model_choice)

    if not gen_result["valid"]:
        return handle_invalid_sql(base, gen_result)

    sql = apply_area_filter(gen_result["sql"])
    base["sql"] = sql

    db_result = execute_query(sql)
    
    if not db_result["success"]:
        return handle_db_error(base, db_result)

    return handle_results(base, sql, db_result)






