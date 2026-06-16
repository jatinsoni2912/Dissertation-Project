import time
from llm_pipeline import generate_sql
from mcp_pipeline import generate_sql_with_mcp
from database import execute_query

test_queries = [
    "Where can I go cycling in Edinburgh?",
    "Find parks near Ferry Road",
    "How many post offices are in Edinburgh?",
    "Where can I walk my dog near Leith?",
    "Find cafes within 500 metres of Princes Street",
    "Find restaurants in Stockbridge"
]