import re

def quote_sql_identifiers(sql):
    return re.sub(r'(?<!["\w])natural(?!["\w])', '"natural"', sql, flags=re.IGNORECASE)