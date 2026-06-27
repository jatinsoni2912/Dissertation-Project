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
    os.path.join(os.path.dirname(__file__), "mcp_server.py")
)

async def call_tool_async(tool_name: str, arguments: dict) -> str:
    server_params = StdioServerParameters(command=sys.executable, args=[SERVER_PATH])
   
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(name=tool_name, arguments=arguments)
            
            if result and getattr(result, "content", None):
                return getattr(result.content[0], "text", "") or "{}"
            
            return json.dumps({"success": False, "error": f"Empty response from {tool_name}."})