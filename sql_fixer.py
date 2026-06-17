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

        if not self.is_city_wide and self.lon is not None and self.lat is not None:
            self.rebuild_from_boundary_join()
            self.inject_missing_spatial_filter()

        self.fix_intersects_proximity()
        self.fix_sport_hstore()

        if self.is_city_wide:
            self.strip_city_wide_dwithin()

        self.fix_landuse_tags()
        self.fix_leisure_table()
        self.fix_broken_join()

        if 'COUNT(' not in self.sql.upper() and 'LIMIT' not in self.sql.upper():
            self.sql = self.sql.rstrip(';') + ';'

        return self.sql, self.fixes
