from constants import STREET_SUFFIXES, EXCLUDE_ROUTES_CLAUSE, ORDER_BY_NAME_MATCH
from database import get_connection

def is_street_name(location_name):
    words = location_name.lower().strip().split()
    return any(word in STREET_SUFFIXES for word in words)

def find_street_exact(cur, location_name):
    sql = "SELECT ST_X(ST_Centroid(way)) AS lon, ST_Y(ST_Centroid(way)) AS lat, name FROM planet_osm_line WHERE LOWER(name) = LOWER(%s) AND name IS NOT NULL " + EXCLUDE_ROUTES_CLAUSE + " LIMIT 1"
    cur.execute(sql, (location_name,))
    return cur.fetchone()

def find_street_word_boundary(cur, location_name):
    sql = "SELECT ST_X(ST_Centroid(way)) AS lon, ST_Y(ST_Centroid(way)) AS lat, name FROM planet_osm_line WHERE name ~* ('\\y' || %s || '\\y') AND name IS NOT NULL " + EXCLUDE_ROUTES_CLAUSE + " ORDER BY LENGTH(name) ASC LIMIT 1"
    cur.execute(sql, (location_name,))
    return cur.fetchone()

def find_street_partial(cur, location_name):
    sql = "SELECT ST_X(ST_Centroid(way)) AS lon, ST_Y(ST_Centroid(way)) AS lat, name FROM planet_osm_line WHERE name ILIKE %s AND name IS NOT NULL " + EXCLUDE_ROUTES_CLAUSE + " ORDER BY (LOWER(name) = LOWER(%s)) DESC, LENGTH(name) ASC LIMIT 1"
    cur.execute(sql, (f"%{location_name}%", location_name))
    return cur.fetchone()

def find_street(cur, location_name):
    for finder in (find_street_exact, find_street_word_boundary, find_street_partial):
        result = finder(cur, location_name)

        if result:
            return result
        
    return None

def find_neighbourhood(cur, location_name):
    sql = "SELECT ST_X(ST_Centroid(way)) AS lon, ST_Y(ST_Centroid(way)) AS lat, name FROM planet_osm_polygon WHERE (name ILIKE %s OR name ~* ('\\y' || %s || '\\y')) AND place IN ('suburb','neighbourhood','quarter','village','town') ORDER BY (LOWER(name) = LOWER(%s)) DESC, (name ~* ('\\y' || %s || '\\y')) DESC, ST_Area(way::geography) DESC LIMIT 1"
    cur.execute(sql, (f"%{location_name}%", location_name, location_name, location_name))
    return cur.fetchone()


def find_polygon_boundary(cur, location_name):
    sql = "SELECT ST_X(ST_Centroid(way)) AS lon, ST_Y(ST_Centroid(way)) AS lat, name FROM planet_osm_polygon WHERE (name ILIKE %s OR name ~* ('\\y' || %s || '\\y')) AND way IS NOT NULL ORDER BY (LOWER(name) = LOWER(%s)) DESC, (name ~* ('\\y' || %s || '\\y')) DESC, LENGTH(name) ASC, ST_Area(way::geography) DESC LIMIT 1"
    cur.execute(sql, (f"%{location_name}%", location_name, location_name, location_name))
    return cur.fetchone()


def find_point_of_interest(cur, location_name):
    sql = "SELECT ST_X(way) AS lon, ST_Y(way) AS lat, name FROM planet_osm_point WHERE (name ILIKE %s OR name ~* ('\\y' || %s || '\\y')) " + ORDER_BY_NAME_MATCH + " LIMIT 1"
    cur.execute(sql, (f"%{location_name}%", location_name, location_name, location_name))
    return cur.fetchone()


def find_line_fallback(cur, location_name):
    sql = "SELECT ST_X(ST_Centroid(way)) AS lon, ST_Y(ST_Centroid(way)) AS lat, name FROM planet_osm_line WHERE (name ILIKE %s OR name ~* ('\\y' || %s || '\\y')) AND name IS NOT NULL " + ORDER_BY_NAME_MATCH + " LIMIT 1"
    cur.execute(sql, (f"%{location_name}%", location_name, location_name, location_name))
    return cur.fetchone()

def geocode_location(location_name, conn=None):

    is_local_conn = conn is None
    if is_local_conn:
        conn = get_connection()

    cur = conn.cursor()
    try:
        street_like = is_street_name(location_name)

        result = find_street(cur, location_name) if street_like else None
        if not result:
            result = find_neighbourhood(cur, location_name)
        if not result:
            result = find_polygon_boundary(cur, location_name)
        if not result:
            result = find_point_of_interest(cur, location_name)
        if not result and not street_like:
            result = find_line_fallback(cur, location_name)

        return result
    finally:
        cur.close()
        if is_local_conn:
            conn.close()