
import streamlit as st

EXAMPLE_QUERIES = ["Where can I go cycling in Edinburgh?",
    "Find parks near the city centre",
    "How many post offices are in Edinburgh?",
    "Where can I walk my dog near Leith?",
    "Find cafes within 500 metres of Princes Street",
    "Show me swimming pools in Edinburgh",
    "Find restaurants in Stockbridge",
    "Where can I play football near Newington?"]

EDINBURGH_CENTER = [55.9533, -3.1883]

FEATURE_COLOuRS = {
    'park': '#2d6a4f',
    'garden': '#40916c',
    'cycleway': '#e07b39',
    'footway': '#6b8f71',
    'path': '#6b8f71',
    'cafe': '#c9a84c',
    'restaurant': '#c9a84c',
    'pub': '#9b6b3a',
    'post_office': '#1a2744',
    'library': '#4a5568',
    'museum': '#7c5cbf',
    'swimming_pool': '#3a86ff',
    'pitch': '#52b788',
    'track': '#52b788',
    'sports_centre': '#52b788',
    'golf_course': '#95d5b2',
    'parking': '#adb5bd',
    'default': '#c9a84c'
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
    background: #f8f6f0;
    border: 1px solid rgba(26,39,68,0.08);            
    border-radius: 8px;
    padding: 0.75rem 1rem;
    white-space: pre-wrap;
    color: var(--edinburgh-navy);
    word-break: break-all;
}

.info-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: rgba(201,168,76,0.15);
    color: var(--edinburgh-navy);
    border: 1px solid rgba(201,168,76,0.4);
    border-radius: 999px;
    padding: 0.2rem 0.65rem;
    font-size: 0.78rem;
    font-weight: 500;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}
                
.stTextInput > div > div > input {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    border-radius: 10px !important;
    border: 1.5px solid rgba(26,39,68,0.2) !important;
    padding: 0.65rem 1rem !important;
    background: white !important;
    color: var(--edinburgh-navy) !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--edinburgh-gold) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.2) !important;
}

.stButton > button {
    background: var(--edinburgh-navy) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.5rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: var(--edinburgh-gold) !important;
    color: var(--edinburgh-navy) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(201,168,76,0.35) !important;
}

.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1.5px solid rgba(26,39,68,0.2) !important;
}

div[data-testid="stExpander"] {
    border: 1px solid rgba(26,39,68,0.1) !important;
    border-radius: 10px !important;
    background: white !important;
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

.fix-tag {
    display: inline-block;
    background: rgba(157,35,53,0.1);
    color: var(--edinburgh-red);
    border-radius: 4px;
    padding: 0.1rem 0.4rem;
    font-size: 0.75rem;
    font-family: 'DM Mono', monospace;
    margin: 0.15rem 0.15rem 0.15rem 0;
}

.example-chip {
    display: inline-block;
    background: white;
    border: 1px solid rgba(26,39,68,0.15);
    border-radius: 8px;
    padding: 0.35rem 0.75rem;
    font-size: 0.82rem;
    color: var(--edinburgh-slate);
    margin: 0.2rem;
    cursor: pointer;
    transition: all 0.15s ease;
}

.example-chip:hover {
    border-color: var(--edinburgh-gold);
    color: var(--edinburgh-navy);
    background: rgba(201,168,76,0.08);
}

.stSpinner > div { border-top-color: var(--edinburgh-gold) !important; }

footer { display: none !important; }
#MainMenu { display: none !important; }
/* header visible — needed for sidebar toggle button */

section[data-testid="stSidebar"] {
    background-color: var(--edinburgh-navy) !important;
    padding: 1rem 0.5rem;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: white !important;
    font-size: 0.85rem !important;
    padding: 0.4rem 0.75rem !important;
    text-align: left !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--edinburgh-gold) !important;
    color: var(--edinburgh-navy) !important;
    border-color: var(--edinburgh-gold) !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.3) !important;
    color: white !important;
}
</style>

</style>
                
        """, unsafe_allow_html=True)