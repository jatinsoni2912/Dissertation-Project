import ollama
import os
import re
from dotenv import load_dotenv
from database import get_schema, get_ontology_mappings
 
load_dotenv()
 
BLOCKED_KEYWORDS = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
                    'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE', 'EXECUTE']

INVALID_TAG_FIXES = {
    "landuse = 'park'":        "leisure = 'park'",
    "landuse='park'":          "leisure = 'park'",
    "amenity = 'post office'": "amenity = 'post_office'",
    "amenity = 'dog_walking'": "leisure = 'park'",
    "amenity = 'dog walking'": "leisure = 'park'",
    "amenity = 'coffee_shop'": "amenity = 'cafe'",
    "amenity = 'supermarket'": "shop = 'supermarket'",
    "highway = 'bike'":        "highway = 'cycleway'",
    "highway = 'bicycle'":     "highway = 'cycleway'",
    "highway = 'walking'":     "highway = 'footway'",
}

SKIP_WORDS = {
    'me', 'the', 'a', 'an', 'some', 'any', 'good', 'nice', 'best',
    'nearest', 'closest', 'find', 'show', 'where', 'can', 'go', 'get',
    'are', 'there', 'parks', 'cafes', 'restaurants', 'cycling', 'walking',
    'swimming', 'running', 'hiking', 'football', 'tennis', 'within',
    'metres', 'kilometers', 'km', 'miles', 'around', 'along', 'want',
    'like', 'need', 'looking', 'place', 'places', 'area', 'edinburgh',
    'city', 'centre',
}

HARDCODED_LOCATIONS = {
    'city centre':   (-3.1883, 55.9533),
    'leith':         (-3.1716, 55.9784),
    'stockbridge':   (-3.2051, 55.9588),
    'morningside':   (-3.2107, 55.9290),
    'portobello':    (-3.1120, 55.9536),
    'bruntsfield':   (-3.2040, 55.9380),
    'newington':     (-3.1809, 55.9365),
    'holyrood':      (-3.1772, 55.9507),
    'princes street':(-3.1936, 55.9521),
    'the meadows':   (-3.1896, 55.9402),
    'ferry road':    (-3.2497, 55.9671),
}