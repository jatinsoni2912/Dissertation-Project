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
    'walking': 'walking', 'walk': 'walking', 'stroll': 'walking', 'strolling': 'walking',
    'path': 'walking', 'paths': 'walking', 'footpath': 'walking', 'footpaths': 'walking',
    'pedestrian': 'walking', 'on foot': 'walking',
    'dog': 'dog walking', 'dogs': 'dog walking',

    'cycling': 'cycling', 'cycle': 'cycling', 'bike': 'cycling', 'biking': 'cycling',
    'bicycle': 'cycling', 'bicycles': 'cycling', 'cycleway': 'cycling', 'cycleways': 'cycling',
    'cycle path': 'cycling', 'cycle route': 'cycling', 'cycle lane': 'cycling',

    'swimming': 'swimming', 'swim': 'swimming', 'pool': 'swimming', 'pools': 'swimming',
    'swimming pool': 'swimming', 'leisure pool': 'swimming', 'public pool': 'swimming',
    'lido': 'swimming',

    'running': 'running', 'run': 'running', 'jogging': 'running', 'jog': 'running',
    'runner': 'running',

    'hiking': 'hiking', 'hike': 'hiking', 'hill walking': 'hiking', 'trekking': 'hiking',

    'park': 'park', 'parks': 'park', 'green space': 'park', 'green spaces': 'park',
    'garden': 'park', 'gardens': 'park', 'recreation ground': 'park',
    'open space': 'park', 'meadow': 'park', 'common': 'park',

    'football': 'football', 'soccer': 'football', 'pitch': 'football', 'pitches': 'football',
    'five-a-side': 'football', '5-a-side': 'football', 'astroturf': 'football',
    'team sport': 'football', 'kick about': 'football',

    'tennis': 'tennis', 'tennis court': 'tennis', 'tennis courts': 'tennis',

    'golf': 'golf', 'golf course': 'golf', 'golf courses': 'golf', 'golf club': 'golf',
    'putting': 'golf', 'driving range': 'golf',

    'cricket': 'cricket', 'cricket ground': 'cricket', 'cricket pitch': 'cricket',

    'pub': 'pub', 'pubs': 'pub', 'bar': 'pub', 'bars': 'pub', 'boozer': 'pub',
    'ale house': 'pub', 'tavern': 'pub', 'inn': 'pub', 'alehouse': 'pub',
    'alcoholic': 'pub', 'beer': 'pub', 'ale': 'pub', 'drink': 'pub',

    'cafe': 'cafe', 'cafes': 'cafe', 'coffee': 'cafe', 'coffee shop': 'cafe',
    'coffee house': 'cafe', 'latte': 'cafe', 'flat white': 'cafe', 'espresso': 'cafe',
    'cappuccino': 'cafe', 'hot drink': 'cafe', 'caffeine': 'cafe', 'tea room': 'cafe',
    'tearoom': 'cafe', 'bakery': 'cafe', 'patisserie': 'cafe',

    'restaurant': 'restaurant', 'restaurants': 'restaurant', 'eating': 'restaurant',
    'eat': 'restaurant', 'dine': 'restaurant', 'dining': 'restaurant', 'dinner': 'restaurant',
    'lunch': 'restaurant', 'food': 'restaurant', 'takeaway': 'restaurant',
    'takeout': 'restaurant', 'eatery': 'restaurant', 'bistro': 'restaurant',
    'brasserie': 'restaurant',

    'hotel': 'hotel', 'hotels': 'hotel', 'accommodation': 'hotel', 'stay': 'hotel',
    'b&b': 'hotel', 'bed and breakfast': 'hotel', 'guesthouse': 'hotel',
    'guest house': 'hotel', 'hostel': 'hotel', 'lodge': 'hotel',

    'museum': 'museum', 'museums': 'museum', 'gallery': 'museum', 'galleries': 'museum',
    'art gallery': 'museum', 'exhibition': 'museum',
    'attraction': 'museum', 'attractions': 'museum', 'tourist': 'museum',
    'sightseeing': 'museum', 'heritage': 'museum', 'historic': 'museum',

    'pharmacy': 'pharmacy', 'pharmacies': 'pharmacy', 'chemist': 'pharmacy',
    'chemists': 'pharmacy', 'drugstore': 'pharmacy', 'dispensary': 'pharmacy',

    'library': 'library', 'libraries': 'library', 'book': 'library',

    'supermarket': 'supermarket', 'supermarkets': 'supermarket', 'grocery': 'supermarket',
    'groceries': 'supermarket', 'food shop': 'supermarket', 'food shops': 'supermarket',
    'weekly shop': 'supermarket', 'shopping': 'supermarket',

    'deprived': 'deprivation', 'deprivation': 'deprivation', 'poorest': 'deprivation',
    'decile': 'deprivation', 'disadvantaged': 'deprivation', 'destitute': 'deprivation',
    'economically': 'deprivation', 'poverty': 'deprivation', 'low income': 'deprivation',
    'underprivileged': 'deprivation', 'most deprived': 'deprivation',
    'least deprived': 'deprivation', 'affluent': 'deprivation', 'wealthy': 'deprivation',
    'richest': 'deprivation',

    'post office': 'post_office', 'post offices': 'post_office', 'postbox': 'post_office',

    'sports centre': 'sports_centre', 'sports centers': 'sports_centre',
    'leisure centre': 'sports_centre', 'leisure centers': 'sports_centre',
    'gym': 'sports_centre', 'fitness': 'sports_centre', 'fitness centre': 'sports_centre',
}


PROXIMITY_RADIUS = {
    
    # small point amenities — dense in cities, 500m is a short walk
    'cafe':           500,
    'pub':            500,
    'bar':            500,
    'restaurant':     750,
    'pharmacy':       750,
    'library':       1000,
    'post_office':   1000,
    'atm':            500,
    
    # larger destination amenities
    'hotel':         2000,
    'museum':        1500,
    'attraction':    1500,
    'supermarket':   1000,
    
    # leisure/sport — polygon features with larger footprints
    'park':          1500,
    'pitch':         3000,
    'golf_course':   5000,
    'swimming_pool': 2000,
    'sports_centre': 2000,
    'nature_reserve':3000,
    
    # default fallback
    'default':       1000,
}
