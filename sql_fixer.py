import re
from sql_extractor import extract_sql
from constants import LANDUSE_CORRECTIONS, LEISURE_POLYGON_TAGS

class SqlFixer:
    def __init__(self, sql, lon=None, lat=None, is_city_wide=False):
        self.sql = extract_sql(sql)
        self.lon = lon
        self.lat = lat
        self.is_city_wide = is_city_wide
        self.fixes = []
    
    def note(self, message):
        self.fixes.append(message)

    def run(self):
        self.fix_geography_casts()
        self.fix_alias_prefix()
