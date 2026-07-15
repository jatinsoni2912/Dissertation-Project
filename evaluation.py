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

def run_single_query(query, index, total, approach_fn, model, provider):
    print(f" [{index:2d}/{total}] {query['query'][:60]}...", end=' ', flush=True)

    t0 = time.time()
    try:
        result = approach_fn(query['query'], model=model)
    except Exception as e:
        result = {'sql': '', 'valid': False, 'fixes_applied': [], 'error': str(e)}
    latency = round(time.time() - t0, 2)

    scores = score_result(result, query)
    scores['latency'] = latency
    scores['query'] = query['query']
    scores['category'] = query['category']
    scores['provider'] = provider
    scores['model'] = model

    status = '✓' if scores['has_results'] or (query['query_type'] == 'count' and scores['exec_success']) else '✗'
    print(f"{status}  {latency}s  rows={scores['row_count']}  fixes={scores['fixes_count']}")
    return scores

def run_approach(queries, approach_fn, approach_label, model, provider):
    os.environ["OLLAMA_PROVIDER"] = provider

    results = []
    for i, q in enumerate(queries, 1):
        scores = run_single_query(q, i, len(queries), approach_fn, model, provider)
        scores['approach'] = approach_label
        results.append(scores)
    return results

def compute_summary_metrics(results):
    n = len(results)

    return {
        'n': n, 'sql_valid': sum(1 for r in results if r['sql_valid']),
        'exec_success': sum(1 for r in results if r['exec_success']),
        'has_results': sum(1 for r in results if r['has_results']),
        'table_correct': sum(1 for r in results if r['table_correct']),
        'tag_correct': sum(1 for r in results if r['tag_correct']),
        'loc_correct': sum(1 for r in results if r['loc_correct']),
        'qtype_correct': sum(1 for r in results if r['qtype_correct']),
        'avg_latency': round(sum(r['latency'] for r in results) / n, 2),
        'avg_fixes': round(sum(r['fixes_count'] for r in results) / n, 1)}

def print_metrics_table(metrics, results, label):
    n = metrics['n']
    pct = lambda count: f"{count}/{n} ({100*count//n}%)"
    provider = results[0].get('provider', '?')
    model = results[0].get('model', '?')

    print(f"\n{'─'*60}")
    print(f" {label}")
    print(f" Provider: {provider}  |  Model: {model}")
    print(f"{'─'*60}")
    print(f" SQL validity {pct(metrics['sql_valid'])}")
    print(f" Execution success {pct(metrics['exec_success'])}")
    print(f" Results returned {pct(metrics['has_results'])}")
    print(f" Table accuracy {pct(metrics['table_correct'])}")
    print(f" Tag accuracy {pct(metrics['tag_correct'])}")
    print(f" Location accuracy {pct(metrics['loc_correct'])}")
    print(f" Query type acc. {pct(metrics['qtype_correct'])}")
    print(f" Avg latency {metrics['avg_latency']}s")
    print(f" Avg fixes applied {metrics['avg_fixes']}")
    print(f"{'─'*60}")

def print_category_breakdown(results):
    cat_results = defaultdict(lambda: {'total': 0, 'passed': 0})
    
    for r in results:
        cat = r.get('category', 'unknown')
        cat_results[cat]['total'] += 1
        passed = r['has_results'] or (r['exec_success'] and 'count' in cat)
        if passed:
            cat_results[cat]['passed'] += 1

    if len(cat_results) <= 1:
        return

    print(f"\n Results by category:")
    for cat in sorted(cat_results):
        c = cat_results[cat]
        bar = '✓' * c['passed'] + '✗' * (c['total'] - c['passed'])
        print(f" {cat:<30} {c['passed']}/{c['total']}  {bar}")
    print(f"{'─'*60}")

def print_summary(results, label):
    if len(results) == 0:
        return
    
    metrics = compute_summary_metrics(results)
    print_metrics_table(metrics, results, label)
    print_category_breakdown(results)

def print_failures(results, label):
    failures = [r for r in results if not r['has_results'] and not (r['exec_success'] and 'count' in r.get('category',''))]
    if not failures:
        print(f"\n  {label}: no failures!")
        
        return
    
    print(f"\n {label} — failed queries ({len(failures)}):")
    
    for r in failures:
        print(f"• {r['query'][:60]}")
        print(f" SQL: {r['sql'][:100]}")
        if r['error']:
            print(f" Error: {r['error'][:80]}")

def save_csv(all_results, filename):
    fields = ['provider', 'model', 'approach', 'category', 'query', 'latency', 'sql_valid', 'exec_success', 'has_results', 'table_correct', 'tag_correct', 'loc_correct', 'qtype_correct', 'row_count', 'fixes_count', 'sql', 'error']
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        
        for r in all_results:
            w.writerow(r)
    
    print(f"\n  Results saved to {filename}")

def build_arg_parser():
    parser = argparse.ArgumentParser(description='GeoQuery evaluation', formatter_class=argparse.RawTextHelpFormatter)

