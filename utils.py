def classify_query(terms, query):
    is_dep = 'deprivation' in terms or any(
        x in query for x in ('deprived', 'deprivation', 'decile', 'affluent')
    )
    return {
        'is_count': any(x in query for x in ('how many', 'count', 'number of')),
        'is_dep':   is_dep,
        'is_cross': is_dep and any(
            x in query for x in
            ('cafe', 'park', 'cycle', 'pub', 'restaurant', 'shop', 'library', 'swim')
        ),
        'has_limit': bool(re.search(r'show me \d+|find \d+|\d+\s+(?:cafes?|parks?|pubs?)', query)),
        'has_sport': any(s in terms for s in SPORTS),
    }