STREET_SUFFIXES = {
    'road','street','lane','avenue','drive','crescent','place',
    'rd','st','ave','mile','wynd','close','gate','terrace',
    'grove','walk','row','gardens','court','way','path',
    'vennel','loan','brae','hill','bank','view','park',
    'square','circus','quay','bridge','causeway',
}

EXCLUDE_ROUTES_CLAUSE = (
    " AND (route IS NULL OR route NOT IN ('bus','tram','train','subway',"
    "'monorail','light_rail','ferry','bicycle','foot'))"
    " AND name NOT ILIKE 'Bus %%'"
    " AND name NOT ILIKE 'Route %%'"
    " AND name NOT ILIKE 'Cycle Route %%'"
    " AND highway IS NOT NULL"
)

ORDER_BY_NAME_MATCH = """
    ORDER BY (LOWER(name) = LOWER(%s)) DESC, 
             (name ~* ('\\y' || %s || '\\y')) DESC, 
             LENGTH(name) ASC
"""

CITY_WIDE_SIGNALS = {
    'in edinburgh', 'across edinburgh', 'throughout edinburgh',
    'all edinburgh', 'edinburgh wide', 'city wide', 'citywide',
    'deprived areas', 'deprived neighbourhoods', 'deprived parts',
    'least deprived', 'most deprived', 'deprivation decile',
}

BLOCKED_KEYWORDS = [
    'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
    'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE', 'EXECUTE',
]

ACTIVITY_KEYWORDS = {
        'walking': 'walking',   'walk': 'walking',
        'path': 'walking',      'paths': 'walking',
        'cycling': 'cycling',   'cycle': 'cycling',
        'bike': 'cycling',      'biking': 'cycling',
        'swimming': 'swimming', 'swim': 'swimming',
        'running': 'running',   'run': 'running',
        'hiking': 'hiking',     'hike': 'hiking',
        'dog': 'dog walking',   'dog walking': 'dog walking',
        'park': 'park',         'parks': 'park',
        'relaxing': 'relaxing', 'relax': 'relaxing',
        'picnic': 'picnic',
        'football': 'football', 'soccer': 'football',
        'tennis': 'tennis',     'golf': 'golf',
        'basketball': 'basketball', 'cricket': 'cricket',
        'rugby': 'rugby',       'bowls': 'bowls',
        'bowling': 'bowls',     'hockey': 'hockey',
        'netball': 'netball',   'volleyball': 'volleyball',
        'eating': 'eating',     'food': 'eating',
        'restaurant': 'eating', 'drinking': 'drinking',
        'pub': 'drinking',      'coffee': 'coffee',
        'cafe': 'coffee',       'shopping': 'shopping',
        'studying': 'studying', 'library': 'studying',
        'sightseeing': 'sightseeing', 'museum': 'sightseeing',
        'parking': 'parking',   'post office': 'post office',
        'healthcare': 'healthcare', 'hospital': 'healthcare',
        'deprived': 'deprivation',      'deprivation': 'deprivation',
        'most deprived': 'deprivation', 'least deprived': 'deprivation',
        'poorest': 'deprivation',       'affluent': 'deprivation',
        'poverty': 'deprivation',       'decile': 'deprivation',
        'low income': 'deprivation',    'high income': 'deprivation',
        'inequality': 'deprivation',    'socioeconomic': 'deprivation',
    }
