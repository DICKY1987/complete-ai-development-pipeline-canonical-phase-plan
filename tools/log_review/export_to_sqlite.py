#!/usr/bin/env python3
"""
Export aggregated logs to SQLite database.
Python-based exporter that doesn't require System.Data.SQLite DLL.
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime
import argparse


def create_database(db_path: Path, logs: list):
    """Create SQLite database and insert logs."""
    print(f"Creating SQLite database: {db_path}")
    
    # Remove existing database
    if db_path.exists():
        db_path.unlink()
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool TEXT NOT NULL,
            type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            session_id TEXT,
            data_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tool ON logs(tool)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_type ON logs(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON logs(session_id)")
    
    # Create summary table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summary (
            tool TEXT PRIMARY KEY,
            total_entries INTEGER,
            unique_sessions INTEGER,
            unique_types INTEGER,
            first_entry TEXT,
            last_entry TEXT
        )
    """)
    
    # Insert logs
    print(f"Inserting {len(logs)} log entries...")
    for i, log in enumerate(logs, 1):
        cursor.execute("""
            INSERT INTO logs (tool, type, timestamp, session_id, data_json)
            VALUES (?, ?, ?, ?, ?)
        """, (
            log.get('tool'),
            log.get('type'),
            log.get('timestamp'),
            log.get('sessionId'),
            json.dumps(log.get('data', {}))
        ))
        
        if i % 100 == 0:
            print(f"  Inserted {i} entries...", end='\r')
    
    print(f"  Inserted {len(logs)} entries    ")
    
    # Generate summary data
    cursor.execute("""
        INSERT INTO summary (tool, total_entries, unique_sessions, unique_types, first_entry, last_entry)
        SELECT 
            tool,
            COUNT(*) as total_entries,
            COUNT(DISTINCT session_id) as unique_sessions,
            COUNT(DISTINCT type) as unique_types,
            MIN(timestamp) as first_entry,
            MAX(timestamp) as last_entry
        FROM logs
        GROUP BY tool
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✓ Database created successfully")
    return db_path


def main():
    parser = argparse.ArgumentParser(description='Export aggregated logs to SQLite')
    parser.add_argument('log_file', nargs='?', help='JSONL log file to export')
    parser.add_argument('-o', '--output', help='Output database file')
    args = parser.parse_args()
    
    # Find latest log file if not specified
    if not args.log_file:
        aggregated_dir = Path('aggregated')
        if aggregated_dir.exists():
            log_files = sorted(aggregated_dir.glob('aggregated-*.jsonl'), key=lambda p: p.stat().st_mtime, reverse=True)
            if log_files:
                args.log_file = str(log_files[0])
            else:
                print("Error: No aggregated log files found in ./aggregated/")
                return 1
        else:
            print("Error: ./aggregated/ directory not found")
            return 1
    
    log_file = Path(args.log_file)
    if not log_file.exists():
        print(f"Error: Log file not found: {log_file}")
        return 1
    
    # Determine output path
    if args.output:
        db_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        exports_dir = Path('exports')
        exports_dir.mkdir(exist_ok=True)
        db_path = exports_dir / f"ai-logs-{timestamp}.db"
    
    print(f"\nAI Tools Log Exporter (Python)")
    print("=" * 70)
    print(f"Source: {log_file.name}")
    print(f"Output: {db_path}")
    print()
    
    # Load logs
    print(f"Loading logs from {log_file}...")
    logs = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                log = json.loads(line.strip())
                logs.append(log)
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON on line {line_num}: {e}")
    
    print(f"Loaded {len(logs)} log entries")
    print()
    
    # Create database
    create_database(db_path, logs)
    
    # Show file size
    db_size_kb = db_path.stat().st_size / 1024
    print(f"\nDatabase size: {db_size_kb:.2f} KB")
    
    # Show example queries
    print("\n" + "=" * 70)
    print("Example SQL queries:")
    print("=" * 70)
    print()
    print("# Summary by tool")
    print(f"sqlite3 '{db_path}' 'SELECT * FROM summary;'")
    print()
    print("# Recent conversations")
    print(f"sqlite3 '{db_path}' 'SELECT tool, type, timestamp, session_id FROM logs WHERE type=\"conversation\" ORDER BY timestamp DESC LIMIT 10;'")
    print()
    print("# Session activity")
    print(f"sqlite3 '{db_path}' 'SELECT session_id, COUNT(*) as count FROM logs WHERE session_id IS NOT NULL GROUP BY session_id ORDER BY count DESC LIMIT 10;'")
    print()
    print("# Entries by date")
    print(f"sqlite3 '{db_path}' 'SELECT DATE(timestamp) as date, COUNT(*) as count FROM logs GROUP BY date ORDER BY date DESC;'")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
