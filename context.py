import re

PATTERNS = [
    r'\b(that|the)\s+(hospital|clinic|cafe|pub|restaurant|hotel|museum|park|school|'
    r'library|shop|place|spot|location|building|site)\b',
    r'\b(nearest|closest|near|close)\s+to\s+(it|that|there|this)\b',
    r'\bfrom\s+(there|that|it|here)\b',
    r'\bnear\s+(it|that|there)\b',
    r'\bto\s+that\b',
    r'\bthe\s+same\s+(area|location|place|spot)\b',
    r'\b(close\s+by|nearby)\b',
]
COMPILED = [re.compile(p, re.IGNORECASE) for p in PATTERNS]
