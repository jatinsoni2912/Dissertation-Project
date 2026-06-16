import os
import re
import subprocess
import ollama
import psycopg2
from dotenv import load_dotenv

from database import get_ontology_mappings

from llm_pipeline import (
    extract_activity_terms,
    extract_location,
    validate_sql
)

load_dotenv()

MCP_SERVER_HOST = os.getenv('MCP_HOST', 'localhost')
MCP_SERVER_PORT = int(os.getenv('MCP_PORT', '5432'))

DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

def get_live_schema_via_mcp() -> str:
   
    try:
        # Attempt to call the Node.js MCP server via npx
        result = subprocess.run(
            [
                'npx', '@modelcontextprotocol/server-postgres',
                DB_URL,
                '--query', 'list-tables'
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and result.stdout:
            return result.stdout.strip()

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Fallback — return static schema if MCP server is unavailable
    print("[MCP] Server unavailable — falling back to static schema")


