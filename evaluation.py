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

def check_tag_accuracy(sql, sql_lower, expected):
    exp_key = expected['expected_key']
    exp_value = expected['expected_value']

    if exp_key == 'la_decile':
        return 'la_decile' in sql_lower and exp_value in sql

    return (f"{exp_key} = '{exp_value}'" in sql_lower or f"{exp_key}='{exp_value}'" in sql_lower or f"{exp_key} ilike '%{exp_value}%'" in sql_lower)

def check_location_accuracy(sql_upper, expected):
    exp_loc = expected['location_type']

    if exp_loc == 'city_wide':
        return 'ST_DWITHIN' not in sql_upper and 'ST_MAKEPOINT' not in sql_upper

    if exp_loc == 'named_area':
        return ('ST_DWITHIN' in sql_upper or 'ST_MAKEPOINT' in sql_upper ('JOIN' in sql_upper and 'BOUNDARY' in sql_upper) or 'ILIKE' in sql_upper)

    return 'ST_DWITHIN' in sql_upper or 'ST_MAKEPOINT' in sql_upper 

def check_query_type_accuracy(sql_upper, expected):
    if expected['query_type'] == 'count':
        return 'COUNT(' in sql_upper
    return 'COUNT(' not in sql_upper

def score_result(result, expected):
    sql = result.get('sql', '')
    sql_lower = sql.lower()
    sql_upper = sql.upper()
    sql_valid = result.get('valid', False)

    rows, exec_success, error_msg = get_execution_outcome(result, sql, sql_valid)
    has_results = exec_success and len(rows) > 0
    fixes = result.get('fixes_applied', [])

    return {
        'sql_valid': sql_valid,
        'exec_success': exec_success,
        'has_results': has_results,
        'table_correct': check_table_accuracy(sql_lower, expected),
        'tag_correct': check_tag_accuracy(sql, sql_lower, expected),
        'loc_correct': check_location_accuracy(sql_upper, expected),
        'qtype_correct': check_query_type_accuracy(sql_upper, expected),
        'row_count': len(rows), 'fixes_count': len(fixes), 'fixes': fixes, 'sql': sql, 'error': error_msg}