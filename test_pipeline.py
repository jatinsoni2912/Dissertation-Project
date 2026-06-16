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

USE_MCP_PIPELINE = False 

print("=" * 60)
print(f"STARTING PIPELINE BENCHMARK (MCP Enabled: {USE_MCP_PIPELINE})")
print("=" * 60)

pipeline_total_start = time.perf_counter()

for idx, query in enumerate(test_queries, 1):
    print(f"\n[{idx}/{len(test_queries)}] QUERY: {query}")
    print("-" * 50)
    
    llm_start = time.perf_counter()
    if USE_MCP_PIPELINE:
        result = generate_sql_with_mcp(query)
    else:
        result = generate_sql(query)
    llm_duration = time.perf_counter() - llm_start
    
    print(f"SQL Generated:\n  {result['sql']}")
    print(f"Valid Alignment Check: {result['valid']}")
    print(f"Activity Terms Found: {result['activity_terms_found']}")
    print(f"Location Resolved: {result['location_resolved']}")
    
    db_duration = 0.0
    if result['valid']:
        db_start = time.perf_counter()
        db_result = execute_query(result['sql'])
        db_duration = time.perf_counter() - db_start
        
        if db_result['success']:
            print(f"Database Execution: SUCCESS ({len(db_result['results'])} rows returned)")
        else:
            print(f"Database Execution: FAILED (Error: {db_result['error']})")
    else:
        print("Database Execution: SKIPPED (Invalid SQL structure or unsafe keywords)")

    total_query_duration = llm_duration + db_duration
    print(f"\n--- Timing Profile ---")
    print(f"  LLM Gen Time: {llm_duration:.4f} seconds")
    print(f"  DB Exec Time: {db_duration:.4f} seconds")
    print(f"  Total Time:   {total_query_duration:.4f} seconds")
    print("-" * 50)

pipeline_total_duration = time.perf_counter() - pipeline_total_start
print("\n" + "=" * 60)
print(f"BENCHMARK COMPLETE | Total Benchmark Run Time: {pipeline_total_duration:.2f} seconds")
print("=" * 60)