import re

def extract_sql(text):
    text = re.sub(r'```sql\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()

    if text.upper().startswith('SELECT'):
        return text

    match = re.search(r'(SELECT\s+.+?)(?:\n\n|\Z)', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    match = re.search(r'(SELECT\b.+)', text, re.DOTALL | re.IGNORECASE)
    if match:
        extracted = match.group(1).strip()
        semi = re.search(r'^(.*?;)', extracted, re.DOTALL)
        return semi.group(1).strip() if semi else extracted

    return text