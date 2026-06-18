def build_tag_section(available_tags):
    if not available_tags:
        return ""
    lines = ["REAL TAG VALUES IN THIS DATABASE — use ONLY these values:"]
    leisure_vals = available_tags.get('leisure_poly', [])
    if leisure_vals:
        quoted = ", ".join(f"'{v}'" for v in leisure_vals[:6])
        lines.append(f"  RULE: {quoted} use leisure= key (NOT amenity=)")
    if available_tags.get('amenity'):
        lines.append(f"  amenity (planet_osm_point): {', '.join(available_tags['amenity'][:20])}")
    if leisure_vals:
        lines.append(f"  leisure (planet_osm_polygon): {', '.join(leisure_vals[:15])}")
    if available_tags.get('highway'):
        lines.append(f"  highway (planet_osm_line): {', '.join(available_tags['highway'][:8])}")
    return "\n".join(lines) + "\n"

def build_location_rule(location_name, lon, lat, is_city_wide, is_named_area, search_radius):
    if is_city_wide:
        return (
            "CRITICAL LOCATION RULE:\n"
            "- This is a CITY-WIDE global search across all of Edinburgh.\n"
            "- DO NOT use ST_DWithin or any coordinate filters.\n"
            "- DO NOT use ST_MakePoint."
        )
    if is_named_area:
        return (
            "CRITICAL LOCATION RULE:\n"
            f"- This query is for the named neighbourhood/area '{location_name}'.\n"
            "- YOU MUST use a spatial JOIN with the boundary polygon (see Examples).\n"
            f"- Filter the boundary table using: boundary.name ILIKE '%{location_name}%'\n"
            "- Do NOT use ST_DWithin or ST_MakePoint."
        )
    return (
        "CRITICAL LOCATION RULE:\n"
        f"- This query is localized near {location_name}.\n"
        f"- YOU MUST use: ST_DWithin(way::geography, ST_MakePoint({lon:.6f},{lat:.6f})::geography, {search_radius})\n"
        f"- Radius is pre-calculated as {search_radius}m — use exactly this value.\n"
        f"- DO NOT add a filter like name = '{location_name}'. The spatial coordinates handle the location perfectly."
    )

def build_prompt(user_query, dynamic_tag_hints, schema, location_name,
                 lon, lat, is_city_wide=False, is_named_area=False,
                 search_radius=1500, examples=None, available_tags=None):

    tag_section = build_tag_section(available_tags)
    location_rule = build_location_rule(location_name, lon, lat, is_city_wide, is_named_area, search_radius)

    return f"""You are a PostGIS expert. Return ONLY valid SQL queries. No text, no markdown.

SCHEMA:
{schema}

{dynamic_tag_hints}
{tag_section}
RULES:
- Output ONLY a raw SELECT query string. Do not use code blocks.
- Always cast geometry using ::geography.
- Count queries must use SELECT COUNT(*) and have NO limit.
- Non-count queries: do NOT add LIMIT — return all results.
- Sports pitches are ALWAYS in planet_osm_polygon with leisure='pitch'. NEVER use planet_osm_line for pitches.
- For specific sports use: AND sport ILIKE '%football%' — sport is a plain text column, NOT an hstore tag.
- Parks, gardens, swimming pools, sports centres are ALWAYS in planet_osm_polygon. NEVER use planet_osm_line for these.
- DEPRIVATION TABLE: edinburgh_deprivation has columns dzname, la_decile, la_rank, geom (EPSG:4326)
- la_decile: 1=most deprived, 10=least deprived
- For deprivation cross-queries JOIN edinburgh_deprivation d ON ST_Intersects(p.way, d.geom)
- Always use d.geom (not d.way) for the deprivation geometry column

{location_rule}

EXAMPLES:
{examples}

NOW GENERATE SQL:
Q: {user_query}
A:"""