import re
import json
import streamlit as st

PATTERNS = [
    r'\b(that|the)\s+(hospital|clinic|cafe|pub|restaurant|hotel|museum|park|school|'
    r'library|shop|place|spot|location|building|site)\b',
    r'\b(nearest|closest|near|close)\s+to\s+(it|that|there|this)\b',
    r'\bfrom\s+(there|that|it|here)\b',
    r'\bnear\s+(it|that|there)\b',
    r'\bto\s+that\b',
    r'\bthe\s+same\s+(area|location|place|spot)\b',
    r'\b(close\s+by|nearby)\b',
]
COMPILED = [re.compile(p, re.IGNORECASE) for p in PATTERNS]

def has_reference(query):
    return any(p.search(query) for p in COMPILED)

def extract_coordinates(results, columns):
    if not results or not columns:
        return None
    try:
        
        geom_idx = None
        for i, col in enumerate(columns):
            if col.lower() in ("st_asgeojson", "geometry", "geom"):
                geom_idx = i
                break
        
        name_idx = None
        for i, col in enumerate(columns):
            if col.lower() == "name":
                name_idx = i
                break

        if geom_idx is None:
            return None
        
        row = results[0]
        geojson = json.loads(row[geom_idx])
        coords = geojson.get('coordinates', [])
        gtype = geojson.get('type', '')
        name = row[name_idx] if name_idx is not None else None
        
        if gtype == 'Point':
            return float(coords[0]), float(coords[1]), name
        
        if gtype in ('Polygon', 'MultiPolygon'):
            flat = coords[0] if gtype == 'Polygon' else coords[0][0]
            lons = [c[0] for c in flat]
            lats = [c[1] for c in flat]
            return sum(lons) / len(lons), sum(lats) / len(lats), name
        
        if gtype == 'LineString':
            mid = len(coords) // 2
            return float(coords[mid][0]), float(coords[mid][1]), name
        
    except Exception:
        pass
    return None

def resolve_location_history(query):
    history = st.session_state.get('context_history', [])
    
    if not history or not has_reference(query):
        return None
    
    for entry in reversed(history):
        if entry.get('result_lon') is not None:
            name = entry.get('result_name') or entry.get('location_name', 'previous result')
            return name, entry['result_lon'], entry['result_lat']
        
        if entry.get('lon') is not None:
            return entry.get('location_name', 'previous location'), entry['lon'], entry['lat']
    return None

def build_context_note(query):
    history = st.session_state.get('context_history', [])
    
    if not history or not has_reference(query):
        return query
    
    last = history[-1]
    ref  = last.get('result_name') or last.get('location_name', '')
    prev = last.get('query', '')
    
    if ref:
        return f"[Context: previous query was '{prev}', top result was '{ref}'] {query}"
    return query

def update_context_history(user_query, location_resolved, results, columns, is_count):
    coords = extract_coordinates(results if not is_count else [],columns if not is_count else [])
    
    entry = {
        'query':         user_query,
        'location_name': location_resolved,
        'lon':           None,
        'lat':           None,
        'result_name':   coords[2] if coords else None,
        'result_lon':    coords[0] if coords else None,
        'result_lat':    coords[1] if coords else None,
    }
    
    history = st.session_state.get('context_history', [])
    history.append(entry)
    st.session_state.context_history = history[-3:]