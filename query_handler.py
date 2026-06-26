import json
import re
import streamlit as st

from database import execute_query, get_feature_locations_for_count
from app_utils import prepare_geojson_collection
from mcp_pipeline import generate_sql_with_mcp
from llm_pipeline import generate_sql

def inject_area_filter(sql):
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

def generate_sql(user_query: str, approach_choice: str, model_choice: str):
    
    if "MCP" in approach_choice:
        from mcp_pipeline import generate_sql_with_mcp
        gen_result = generate_sql_with_mcp(user_query, model=model_choice)
        label = "LLM + MCP"
    else:
        gen_result = generate_sql(user_query, model=model_choice)
        label = "LLM only"

    return gen_result, label

def build_base_metadata(gen_result: dict, approach_label: str, model_choice: str):
    
    return {
        "sql": gen_result["sql"],
        "ontology_used": gen_result.get("ontology_used", False),
        "activity_terms": gen_result.get("activity_terms_found", []),
        "location": gen_result.get("location_resolved", ""),
        "approach": approach_label,
        "fixes": gen_result.get("fixes_applied", []),
        "classification": gen_result.get("classification"),
        "model_used": model_choice,
    }

def handle_invalid_sql(base: dict, gen_result: dict):
    return {
        **base,
        "row_count": 0,
        "is_count": False,
        "error": gen_result["validation_message"],
        "geojson_data": {"type": "FeatureCollection", "features": []},
    }

def handle_db_error(base: dict, db_result: dict):
    return {
        **base,
        "row_count": 0,
        "is_count": False,
        "error": db_result["error"],
        "geojson_data": {"type": "FeatureCollection", "features": []},
    }

def is_count_query(columns: list[str]):
    if not columns:
        return False
    col = columns[0].lower()
    return col in ("count", "total", "count_big") or "count" in col

def handle_count_query(base: dict, sql: str, results: list, columns: list):
    count_value = results[0][0] if results else 0

    loc_rows = get_feature_locations_for_count(sql)
    if loc_rows:
        geojson, _ = prepare_geojson_collection(loc_rows, ["name", "geometry"])
    else:
        geojson = {"type": "FeatureCollection", "features": []}

    return {
        **base,
        "row_count": count_value,
        "is_count": True,
        "count_value": count_value,
        "results": results,
        "columns": columns,
        "geojson_data": geojson,
    }

def handle_feature_query(base: dict, results: list, columns: list):
    geojson, feature_count = prepare_geojson_collection(results, columns)
    return {
        **base,
        "row_count": feature_count,
        "is_count": False,
        "results": results,
        "columns": columns,
        "geojson_data": geojson,
    }


def handle_results(base: dict, sql: str, db_result: dict):
    results = db_result["results"]
    columns = db_result["columns"]

    if is_count_query(columns):
        return handle_count_query(base, sql, results, columns)

    return handle_feature_query(base, results, columns)




