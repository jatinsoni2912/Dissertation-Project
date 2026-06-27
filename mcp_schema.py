import asyncio
import os
import sys
import json
import threading
import re

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MCP_AVAILABLE = True

schema_cache: str = ''
schema_is_live: bool = False

READ_ONLY_GUARD = re.compile(
    r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|GRANT|REVOKE)\b', re.IGNORECASE
)

SERVER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "mcp_geo_server.py")
)