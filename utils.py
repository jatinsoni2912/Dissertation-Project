import re
from database import execute_query
from location_geocoder import geocode_location
from typing import Tuple
from constants import (
    BLOCKED_KEYWORDS, SPORTS, SKIP_WORDS, SKIP_PREFIXES,
    CITY_WIDE_SIGNALS, ACTIVITY_KEYWORDS
)

def extract_activity_terms(user_query: str) -> list[str]:
    q = user_query.lower()
    sorted_keywords = sorted(ACTIVITY_KEYWORDS.keys(), key=len, reverse=True)
    return list({ACTIVITY_KEYWORDS[kw] for kw in sorted_keywords if kw in q})

def extract_sql(llm_output: str) -> str:
    clean_text = llm_output.strip()

    markdown_match = re.search(r'```sql\s*(.*?)\s*```', clean_text, re.DOTALL | re.IGNORECASE)
    if markdown_match:
        return markdown_match.group(1).strip()

    generic_fence = re.search(r'```\s*(.*?)\s*```', clean_text, re.DOTALL)
    if generic_fence:
        return generic_fence.group(1).strip()

    return clean_text

def validate_sql(sql: str) -> Tuple[bool, str]:
    
    sql_upper = sql.upper().strip()

    if not sql_upper.startswith('SELECT'):
        return False, "Query must start with SELECT"

    for keyword in BLOCKED_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', sql_upper):
            return False, f"Blocked keyword '{keyword}' found"

    try:
        check = execute_query(f"EXPLAIN {sql}")
        if not check['success']:
            return False, f"PostgreSQL error: {check.get('error', 'Syntax error')}"
        return True, "Valid"
    except Exception as e:
        return False, f"Validation error: {str(e)}"