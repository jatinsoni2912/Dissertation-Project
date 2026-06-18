import re

def quote_sql_identifiers(sql):
    return re.sub(r'(?<!["\w])natural(?!["\w])', '"natural"', sql, flags=re.IGNORECASE)

def remove_unfilled_placeholders(sql):
    patterns = [
        r"\s+AND\s+sport\s+ILIKE\s+'%value%'",
        r"\s+AND\s+sport\s+ILIKE\s+'%sport_name%'",
        r"\s+AND\s+sport\s+=\s+'value'"
    ]
    for pattern in patterns:
        sql = re.sub(pattern, '', sql, flags=re.IGNORECASE)
    return sql

def resolve_contradictory_tags(sql):
    if "leisure = 'swimming_pool'" in sql and '"natural"' in sql:
        sql = re.sub(r'\s+AND\s+"natural"\s*=\s*\'[^\']+\'', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'"natural"\s*=\s*\'[^\']+\'\s+AND\s+', '', sql, flags=re.IGNORECASE)
    return sql

def normalize_boundary_name_wildcards(sql):
    pattern = r"(boundary\.name\s+ILIKE\s+)'([^%']+)'"
    return re.sub(pattern, lambda m: f"{m.group(1)}'%{m.group(2)}%'", sql, flags=re.IGNORECASE)

def remove_invalid_place_values(sql):
    invalid_terms = ["'city centre',", ", 'city centre'", "'city',", ", 'city'"]
    for term in invalid_terms:
        sql = sql.replace(term, "")
    return sql