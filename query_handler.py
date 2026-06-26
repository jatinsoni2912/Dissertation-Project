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

