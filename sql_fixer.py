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
    
    def fix_geography_casts(self):
        sql = self.sql
        if 'ST_DWithin(way,' in sql and 'way::geography' not in sql:
            sql = sql.replace('ST_DWithin(way,', 'ST_DWithin(way::geography,')
            self.note("Added ::geography cast to way")

        def add_cast(m):
            if '::geography' not in m.group(2):
                return m.group(1) + m.group(2) + '::geography' + m.group(3)
            return m.group(0)

        updated = re.sub(
            r'(ST_DWithin\(way::geography,\s*)(ST_MakePoint\([^)]+\))(\s*,)',
            add_cast, sql
        )
        if updated != sql:
            self.note("Added ::geography cast to ST_MakePoint")
            sql = updated

        self.sql = sql

    def fix_alias_prefix(self):
        sql = self.sql
        if (re.search(r'\b(FROM|JOIN)\s+planet_osm_\w+\s+p\b', sql, re.IGNORECASE) 
            and re.search(r'ST_DWithin\(\s*(?<!p\.)way', sql, re.IGNORECASE)):
            self.sql = re.sub(r'ST_DWithin\(\s*(?<!p\.)way', 'ST_DWithin(p.way', sql, flags=re.IGNORECASE)
            self.note("Fixed ambiguous column reference — added p. prefix inside ST_DWithin")

    
    def rebuild_query_from_boundary_join(self):
        sql = self.sql
        if 'ST_DWithin' in sql or 'JOIN' not in sql.upper() or 'boundary' not in sql.lower():
            return

        table_match = re.search(r'FROM\s+(planet_osm_\w+)', sql, re.IGNORECASE)
        if not table_match:
            return

        table = table_match.group(1)
        select_part = "SELECT COUNT(*)" if 'COUNT(' in sql.upper() else "SELECT name, ST_AsGeoJSON(way)"

        tag_parts = []
        where_match = re.search(r'WHERE\s+(.*)', sql, re.IGNORECASE)
        if where_match:
            clause = re.sub(r'LIMIT\s+\d+', '', where_match.group(1), flags=re.IGNORECASE).strip().rstrip(';')
            clause = re.sub(r'\bp\.', '', clause)
            for part in re.split(r'\s+AND\s+', clause, flags=re.IGNORECASE):
                p = part.strip()
                if not any(x in p.lower() for x in ('boundary', 'place', 'st_intersects', 'st_dwithin')):
                    tag_parts.append(p)

        tag_parts.append(f"ST_DWithin(way::geography, ST_MakePoint({self.lon},{self.lat})::geography, 1000)")
        self.sql = f"{select_part} FROM {table} WHERE {' AND '.join(tag_parts)};"
        self.note("Replaced incorrect boundary JOIN with coordinate ST_DWithin")
