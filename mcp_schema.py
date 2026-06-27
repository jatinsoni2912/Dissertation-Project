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

def submit_tool_call(tool_name: str, arguments: dict, timeout: int = 60) -> str:
    if not MCP_AVAILABLE:
        return json.dumps({"success": False, "error": "MCP library not installed."})
    
    try:
        return asyncio.run(asyncio.wait_for(call_tool_async(tool_name, arguments), timeout=timeout))
    
    except asyncio.TimeoutError:
        return json.dumps({"success": False, "error": f"Tool call timed out after {timeout}s."})
    
    except Exception as e:
        return json.dumps({"success": False, "error": f"Tool call '{tool_name}' failed: {str(e)}"})


def run_mcp_query_sync(target_sql: str, timeout: int = 60) -> str:
    if READ_ONLY_GUARD.search(target_sql):
        return json.dumps({"success": False, "error": "Write operations blocked."})
    
    return submit_tool_call(
        "execute_spatial_query", {"sql_query": str(target_sql)}, timeout=timeout
    )