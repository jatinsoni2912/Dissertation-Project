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

def fix_missing_table_aliases(sql):
    if ' p ' in sql and 'JOIN planet_osm_polygon boundary' in sql:
        for col in ['leisure', 'sport', 'amenity', 'highway', 'tourism', 'shop']:
            sql = re.sub(
                rf'(?<!\w)(?<!p\.)(?<!boundary\.)({col}\s*(?:=|ILIKE|IN)\s)',
                lambda m: f'p.{m.group(1)}',
                sql
            )
    return sql


def sanitize_sql(sql):
    
    sql = quote_sql_identifiers(sql)
    sql = remove_unfilled_placeholders(sql)
    sql = resolve_contradictory_tags(sql)
    sql = normalize_boundary_name_wildcards(sql)
    sql = remove_invalid_place_values(sql)
    sql = fix_missing_table_aliases(sql)
    
    return sql.strip()