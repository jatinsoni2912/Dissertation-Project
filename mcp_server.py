import os
import json
import re
import psycopg2
import psycopg2.extras
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

mcp = FastMCP("Edinburgh-PostGIS-Discoverer")
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
