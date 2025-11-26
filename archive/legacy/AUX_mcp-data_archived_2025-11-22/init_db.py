import sqlite3
import sys

# Connect to database
db_path = r'C:\Users\richg\mcp-data\pipeline.db'
schema_path = r'C:\Users\richg\mcp-data\pipeline-schema.sql'

try:
    # Read schema file
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Connect and execute
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    
    print(f"SUCCESS: Database initialized at {db_path}")
    print("Created tables: policy_versions, run_traces, modules, workstreams,")
    print("  planning_items, event_log, safepatch_checkpoints, v_model_gates, plugin_conformance")
    
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
