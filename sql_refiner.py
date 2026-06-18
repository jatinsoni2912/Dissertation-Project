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

