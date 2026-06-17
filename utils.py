import re

from constants import (
    BLOCKED_KEYWORDS, SPORTS, SKIP_WORDS, SKIP_PREFIXES,
    CITY_WIDE_SIGNALS, EXAMPLES, ACTIVITY_FEATURE,
    LANDUSE_CORRECTIONS, LEISURE_POLYGON_TAGS,
)

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


def pick_city_wide_key(terms):
    if 'walking' in terms:     return 'walking_paths'
    if 'running' in terms:     return 'running'
    if any(x in terms for x in ['cycling', 'hiking']):  return 'city_wide_line'
    if any(x in terms for x in ['swimming', 'golf']):   return 'city_wide_polygon'
    return 'city_wide_point'


def pick_example_keys(terms, is_city_wide, is_named_area, flags):
    keys = []
    if flags['is_count']:  keys.append('count')
    if flags['is_cross']:  keys.append('cross_query')
    elif flags['is_dep']:  keys.append('deprivation_only')
    if flags['has_sport']: keys.append('sport_named_area' if is_named_area else 'sport_proximity')
    if flags['has_limit']: keys.append('explicit_limit')

    if is_named_area and not flags['has_sport']:
        keys.append('named_area')
    elif is_city_wide:
        keys.append(pick_city_wide_key(terms))
    elif not flags['is_dep']:
        keys.append(
            'proximity_polygon'
            if any(x in terms for x in ['park', 'swimming', 'golf'])
            else 'proximity_point'
        )
    return keys

def finalise_example_keys(keys):
    seen, chosen = set(), []
    for k in keys:
        if k not in seen and k in EXAMPLES:
            seen.add(k)
            chosen.append(k)
        if len(chosen) == 4:
            break
    if not chosen:
        return ['proximity_point', 'named_area']
    if len(chosen) == 1:
        chosen.append('named_area' if chosen[0] != 'named_area' else 'proximity_point')
    return chosen