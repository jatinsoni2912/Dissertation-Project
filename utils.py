import re
from database import execute_query
from location_geocoder import geocode_location
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