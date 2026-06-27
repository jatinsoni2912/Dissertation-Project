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

def resolve_tags_via_mcp(activity_terms: list[str]) -> str:
    if not MCP_AVAILABLE or not activity_terms:
        return ""

    SKIP_TERMS = {'deprivation', 'dog walking'}
    
    terms = [t for t in activity_terms if t.lower() not in SKIP_TERMS]
    
    if not terms:
        return ""

    raw = submit_tool_call("lookup_feature_tags", {"search_terms": terms}, timeout=15)
    try:
        data = json.loads(raw)
        if not data.get("success") or not data.get("results"):
            return ""
        
        lines = ["VERIFIED OSM TAGS (from live database — use these exact values):"]
        
        for entry in data["results"]:
            term = entry["query_term"]
            matches = entry.get("matches", [])
            if not matches:
                continue
            best = matches[0]
            lines.append(
                f"  - '{term}' → {best['osm_table']}: "
                f"{best['osm_key']} = '{best['osm_value']}'"
            )
            
            for alt in matches[1:]:
                if alt['osm_value'] != best['osm_value']:
                    lines.append(
                        f"    (also: {alt['osm_table']}: "
                        f"{alt['osm_key']} = '{alt['osm_value']}')"
                    )
        return "\n".join(lines) + "\n" if len(lines) > 1 else ""
    
    except Exception:
        return ""
    
def check_citywide_via_mcp(user_query: str) -> bool:
    if not MCP_AVAILABLE:
        return False
    raw = submit_tool_call("is_query_citywide", {"query": user_query}, timeout=5)
    
    try:
        return json.loads(raw).get("is_citywide", False)
    
    except Exception:
        return False