
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

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

:root {
    --edinburgh-navy:   #1a2744;
    --edinburgh-gold:   #c9a84c;
    --edinburgh-stone:  #f4f0e8;
    --edinburgh-slate:  #4a5568;
    --edinburgh-green:  #2d6a4f;
    --edinburgh-red:    #9b2335;
    --radius:           12px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--edinburgh-stone);
    color: var(--edinburgh-navy);
}

.block-container { padding: 1.5rem 2rem 2rem 2rem; max-width: 1400px; }
h1, h2, h3 { font-family: 'DM Serif Display', serif; }

.geoquery-header {
    display: flex; align-items: center; gap: 1rem; margin-bottom: 0.25rem;
}
.geoquery-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem; color: var(--edinburgh-navy); margin: 0; line-height: 1;
}
.geoquery-subtitle {
    font-size: 0.95rem; color: var(--edinburgh-slate);
    margin: 0 0 1.5rem 0; font-weight: 300;
}

.placeholder-box {
    background: white; border: 1.5px dashed rgba(26,39,68,0.25);
    border-radius: var(--radius); padding: 2rem; text-align: center;
    color: var(--edinburgh-slate); font-size: 0.9rem; height: 400px;
    display: flex; align-items: center; justify-content: center;
}

.query-card {
    background: white; border-radius: var(--radius);
    padding: 1.25rem 1.5rem; border: 1px solid rgba(26,39,68,0.1);
    box-shadow: 0 2px 8px rgba(26,39,68,0.06); margin-bottom: 1rem;
}

.stTextInput > div > div > input {
    font-family: 'DM Sans', sans-serif !important; font-size: 1rem !important;
    border-radius: 10px !important; border: 1.5px solid rgba(26,39,68,0.2) !important;
    padding: 0.65rem 1rem !important; background: white !important;
    color: var(--edinburgh-navy) !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--edinburgh-gold) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.2) !important;
}

.stButton > button {
    background: var(--edinburgh-navy) !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important;
    font-size: 0.95rem !important; padding: 0.65rem 1.5rem !important;
    width: 100% !important; transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: var(--edinburgh-gold) !important;
    color: var(--edinburgh-navy) !important; transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(201,168,76,0.35) !important;
}

.stSelectbox > div > div {
    border-radius: 10px !important; border: 1.5px solid rgba(26,39,68,0.2) !important;
}

</style>
"""