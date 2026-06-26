import json
import re
import streamlit as st

from database import execute_query, get_feature_locations_for_count
from app_utils import prepare_geojson_collection

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