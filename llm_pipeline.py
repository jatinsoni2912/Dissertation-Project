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