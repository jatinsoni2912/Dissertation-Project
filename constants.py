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
