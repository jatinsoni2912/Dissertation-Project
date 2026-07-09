
import streamlit as st

EXAMPLE_QUERIES = [
    "Where can I go cycling in Edinburgh?",
    "Find parks near the city centre",
    "How many post offices are in Edinburgh?",
    "Where can I walk my dog near Leith?",
    "Find cafes within 500 metres of Princes Street",
    "Show me swimming pools in Edinburgh",
    "Find restaurants in Stockbridge",
    "Where can I play football near Newington?",
]

EDINBURGH_CENTER = [55.9533, -3.1883]

FEATURE_COLOuRS = {
    'park':          '#2d6a4f',
    'garden':        '#40916c',
    'cycleway':      '#e07b39',
    'footway':       '#6b8f71',
    'path':          '#6b8f71',
    'cafe':          '#c9a84c',
    'restaurant':    '#c9a84c',
    'pub':           '#9b6b3a',
    'post_office':   '#1a2744',
    'library':       '#4a5568',
    'museum':        '#7c5cbf',
    'swimming_pool': '#3a86ff',
    'pitch':         '#52b788',
    'track':         '#52b788',
    'sports_centre': '#52b788',
    'golf_course':   '#95d5b2',
    'parking':       '#adb5bd',
    'default':       '#c9a84c',
}

def apply():
    st.markdown("""

<style>
    
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');
        
:root {
    --edinburgh-navy: #1a2744;
    --edinburgh-gold: #c9a84c;
    --edinburgh-stone: #f4f0e8;
    --edinburgh-slate: #4a5568;
    --edinburgh-green: #2d6a4f;
    --edinburgh-red: #9b2335;
    --radius: 12px;      
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--edinburgh-stone);
    color: var(--edinburgh-navy);}        
            
.geoquery-header { display:flex; align-items:center; gap:1rem; margin-bottom:0.25rem;}
.geoquery-title {font-family:'DM Serif Display',serif; font-size:2.4rem; color:var(--edinburgh-navy); margin:0; line-height:1;}
.geoquery-subtitle {font-size:0.95rem; color: var(--edinburgh-slate); margin:0 0 1.5rem 0; font-weight: 300;}

.query-card {
    background: #fff;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    border: 1px solid rgba(26,39,68,0.1);
    box-shadow: 0 2px 12px rgba(26,39,68,0.08);
    margin-bottom: 1rem;
}
                
.result-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--edinburgh-navy);
    color: white;
    padding: 0.35rem 0.85rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 0.75rem;
    font-family: 'DM Mono', monospace;
}

.result-badge.zero {
    background: var(--edinburgh-red);
}

.result-badge.success {
    background: var(--edinburgh-green);
}
                
.sql-expander {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    background: #f8f9fa;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 0.75rem;
    white-space: pre-wrap;
    color: #2d3748;
}

.info-pill {
    display: inline-block;
    background: #eef2f7;
    color: #1a2744;
    font-size: 0.75rem;
    padding: 2px 10px;
    border-radius: 20px;
    margin: 2px 3px 2px 0;
}

.fix-tag {
    display: inline-block;
    background: #fef3cd;
    color: #856404;
    font-size: 0.78rem;
    padding: 2px 8px;
    border-radius: 4px;
    margin: 2px 4px 2px 0;
}

.stButton > button {border-radius:8px; font-family:'DM Sans',sans-serif; font-weight:500; }
.stTextInput > div > div > input {border-radius:8px; border-color:#c9a84c; }
.stTextInput > div > div > input:focus {border-color:#1a2744; box-shadow:0 0 0 2px rgba(26,39,68,.15); }

</style>
                
        """, unsafe_allow_html=True)