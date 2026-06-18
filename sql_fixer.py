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

    
    def add_missing_spatial_filter(self):
        sql = self.sql
        sql_upper = sql.upper()
        has_spatial = any(x in sql_upper for x in ('ST_DWITHIN', 'ST_INTERSECTS', 'ST_CONTAINS', 'JOIN'))
        if has_spatial:
            return

        spatial = f"ST_DWithin(way::geography, ST_MakePoint({self.lon},{self.lat})::geography, 1000)"
        has_where = 'WHERE' in sql_upper
        has_limit = 'LIMIT' in sql_upper

        if has_where:
            sql = re.sub(r'(?i)\bLIMIT\b', f"AND {spatial} LIMIT", sql) if has_limit \
                else sql.rstrip(';').strip() + f" AND {spatial};"
        else:
            sql = re.sub(r'(?i)\bLIMIT\b', f"WHERE {spatial} LIMIT", sql) if has_limit \
                else sql.rstrip(';').strip() + f" WHERE {spatial};"

        self.sql = sql
        self.note("Injected missing spatial filter")
    
    def fix_intersects_proximity(self):
        sql = self.sql

        prox = r"ST_Intersects\(way,\s*ST_MakePoint\(([^)]+)\)(?:::geography)?\)"
        m = re.search(prox, sql)
        if m:
            sql = re.sub(prox, f"ST_DWithin(way::geography, ST_MakePoint({m.group(1)})::geography, 1000)", sql)
            self.note("Replaced ST_Intersects proximity with ST_DWithin 1000m")

        geo = r"ST_Intersects\(p\.way,\s*ST_MakePoint\(([^)]+)\)::geography\)"
        m = re.search(geo, sql)
        if m:
            sql = re.sub(geo, f"ST_DWithin(p.way::geography, ST_MakePoint({m.group(1)})::geography, 1000)", sql)
            self.note("Replaced ST_Intersects geography point with ST_DWithin 1000m")

        self.sql = sql
    
    def fix_sport_hstore(self):
        sql = self.sql

        def sport_eq(m):
            return f"sport ILIKE '%{m.group(1)}%'"

        def sport_in(m):
            vals = re.findall(r"'([^']+)'", m.group(1))
            return "(" + " OR ".join(f"sport ILIKE '%{v}%'" for v in vals) + ")"

        for pat, fn in [
            (r"tags->>'sport'\s*=\s*'([^']+)'",    sport_eq),
            (r"tags->'sport'\s*=\s*'([^']+)'",     sport_eq),
            (r"tags->>'sport'\s+IN\s*\(([^)]+)\)", sport_in),
            (r"tags->'sport'\s+IN\s*\(([^)]+)\)",  sport_in),
        ]:
            updated = re.sub(pat, fn, sql, flags=re.IGNORECASE)
            if updated != sql:
                self.note("Replaced tags->>'sport' hstore with sport ILIKE column")
                sql = updated

        self.sql = sql
    
    def strip_dwithin_from_city_wide_search(self):
        sql = self.sql
        if 'ST_DWITHIN' in sql.upper():
            self.sql = re.sub(
                r'\s+AND\s+ST_DWithin\s*\([^;]*?::[^;]*?,[^;]*?::[^;]*?,\s*\d+\)',
                '', sql, flags=re.IGNORECASE
            )
            self.note("Stripped ST_DWithin from city-wide query")
    

    def fix_landuse_tags(self):
        sql = self.sql
        for lv, (correct_key, correct_val, correct_table) in LANDUSE_CORRECTIONS.items():
            if f"landuse = '{lv}'" in sql.lower() or f"landuse='{lv}'" in sql.lower():
                sql = re.sub(
                    rf"landuse\s*=\s*'{re.escape(lv)}'",
                    f"{correct_key} = '{correct_val}'",
                    sql, flags=re.IGNORECASE
                )
                if correct_table == 'planet_osm_line':
                    for wrong in ('planet_osm_polygon', 'planet_osm_point'):
                        if wrong in sql.lower():
                            sql = re.sub(wrong, 'planet_osm_line', sql, flags=re.IGNORECASE)
                            break
                self.note(f"Fixed landuse='{lv}' to {correct_key}='{correct_val}'")
        self.sql = sql

    def strip_highway_tags(self, sql):
        for pat in [
            r"highway\s+IN\s*\([^)]+\)\s+AND\s+",
            r"\s+AND\s+highway\s+IN\s*\([^)]+\)",
            r"highway\s*=\s*'[^']+'\s+AND\s+",
            r"\s+AND\s+highway\s*=\s*'[^']+'"
        ]:
            sql = re.sub(pat, '', sql, flags=re.IGNORECASE)
        return re.sub(r'\s{2,}', ' ', sql).strip()
