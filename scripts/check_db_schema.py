"""Check database schema for execution_logs table

DOC_ID: DOC-SCRIPT-SCRIPTS-CHECK-DB-SCHEMA-764
"""

import sqlite3
from pathlib import Path

db_path = Path(".state/orchestration.db")

if not db_path.exists():
    print(f"❌ Database not found: {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))

# List all tables
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

print(f"✓ Database: {db_path}")
print(f"  Tables ({len(tables)}):")
for table in tables:
    print(f"    - {table}")

# Check for execution_logs
print()
if "execution_logs" in tables:
    print("✅ execution_logs table EXISTS")
    cursor = conn.execute("PRAGMA table_info(execution_logs)")
    print("  Schema:")
    for row in cursor.fetchall():
        print(f"    {row[1]}: {row[2]}")
else:
    print("❌ execution_logs table MISSING")
    print("  Action: Need to create table for pattern detector")

conn.close()
