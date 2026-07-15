import argparse
import time
import re
import sys
import json
import os
import csv
from collections import defaultdict
from datetime import datetime

from evaluation_queries import (ALL_QUERIES, ALL_EXTENDED_QUERIES, EXPLICIT_DISTANCE_QUERIES, LANDMARK_PROXIMITY_QUERIES, SPORT_DEPRIVATION_QUERIES)
from database import execute_query
from llm_client import (PROVIDER_OLLAMA, PROVIDER_BEDROCK,  DEFAULT_OLLAMA_MODEL, DEFAULT_BEDROCK_MODEL)
from pure_llm_pipeline import generate_sql_pure_llm, generate_sql_pure_llm_using_bedrock
from llm_pipeline import generate_sql
from mcp_pipeline import generate_sql_with_mcp

APPROACH_PIPELINES = {'0': (generate_sql_pure_llm, 'Approach 0 — Pure LLM'),
    '1': (generate_sql, 'Approach 1 — LLM only (no MCP)'),
    '2': (generate_sql_with_mcp, 'Approach 2 — LLM + MCP')}

QUERY_SETS = {
    'core': (ALL_QUERIES, 'Core ALL'),
    'all': (ALL_EXTENDED_QUERIES + EXPLICIT_DISTANCE_QUERIES + LANDMARK_PROXIMITY_QUERIES + SPORT_DEPRIVATION_QUERIES,'Full set ALL')}

def get_execution_outcome(result, sql, sql_valid):
    if 'mcp_results' in result:
        rows = result.get('mcp_results', [])
        exec_success = result.get('valid', False)
        error_msg = result.get('validation_message', '')
        return rows, exec_success, error_msg

    db_result = execute_query(sql) if sql_valid else {'success': False, 'results': [], 'error': 'invalid SQL'}
    rows = db_result.get('results', [])
    exec_success = db_result.get('success', False)
    error_msg = db_result.get('error', '')
    return rows, exec_success, error_msg

def check_table_accuracy(sql_lower, expected):
    return expected['expected_table'] in sql_lower
