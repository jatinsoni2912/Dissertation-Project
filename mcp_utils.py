import re

BASE_RADIUS = {
    'point_dense':   500,   
    'point_medium':  750,   
    'point_large':  1000,   
    'tourism':      1500,   
    'leisure':      1500,   
    'sport':        3000,   
    'default':      1000,   
}

FEATURE_CATEGORY = {
    'cafe':        ('point_dense',  1.0),
    'pub':         ('point_dense',  1.0),
    'bar':         ('point_dense',  1.0),
    'atm':         ('point_dense',  1.0),
    
    'restaurant':  ('point_medium', 1.0),
    'pharmacy':    ('point_medium', 1.0),
    
    'library':     ('point_large',  1.0),
    'post_office': ('point_large',  1.0),
    'supermarket': ('point_large',  1.0),
    
    'hotel':       ('tourism',      2.0),   
    'museum':      ('tourism',      1.0),   
    'attraction':  ('tourism',      1.0),   
    'guest_house': ('tourism',      1.0),   
    
    'park':            ('leisure', 1.0),   
    'nature_reserve':  ('leisure', 2.0),  
    'swimming_pool':   ('leisure', 1.0),   
    'sports_centre':   ('leisure', 1.0),   
    'playground':      ('leisure', 1.0),   
    
    'pitch':           ('sport',   1.0),   
    'golf_course':     ('sport',   2.0),   
}


