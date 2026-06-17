BLOCKED_KEYWORDS = [
    'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
    'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE', 'EXECUTE',
]

SPORTS = {
    'football', 'soccer', 'cricket', 'tennis', 'rugby',
    'basketball', 'bowls', 'hockey', 'netball', 'volleyball', 'golf',
}

SKIP_WORDS = {
    'me', 'the', 'a', 'an', 'some', 'any', 'good', 'nice', 'best',
    'nearest', 'closest', 'find', 'show', 'where', 'can', 'go', 'get',
    'are', 'there', 'parks', 'cafes', 'restaurants', 'cycling', 'walking',
    'swimming', 'running', 'hiking', 'football', 'tennis', 'within',
    'metres', 'meters', 'kilometers', 'km', 'miles', 'around', 'along',
    'want', 'like', 'need', 'looking', 'place', 'places', 'area',
    'edinburgh', 'city', 'centre', 'near', 'in', 'at', 'of',
    'my', 'dog', 'pub', 'bar', 'cafe', 'shop', 'store',
    'of edinburgh', 'the most', 'the least', 'most deprived', 'least deprived',
    'deprived areas', 'deprived neighbourhoods', 'deprived parts',
}

SKIP_PREFIXES = ('of ', 'the ', 'in the ', 'at the ')