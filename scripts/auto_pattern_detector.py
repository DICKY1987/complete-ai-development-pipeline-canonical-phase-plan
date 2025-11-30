"""CLI script to run pattern automation analysis.

Usage:
    python auto_pattern_detector.py --analyze     # Detect new patterns
    python auto_pattern_detector.py --suggest     # Generate suggestions
    python auto_pattern_detector.py --report      # Weekly report
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-AUTO-PATTERN-DETECTOR-192
# DOC_ID: DOC-SCRIPT-SCRIPTS-AUTO-PATTERN-DETECTOR-129

import argparse
import sqlite3
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from patterns.automation.detectors.execution_detector import ExecutionPatternDetector, analyze_executions
from patterns.automation.analyzers.performance_analyzer import PatternPerformanceAnalyzer
from patterns.automation.detectors.anti_pattern_detector import AntiPatternDetector


def main():
    parser = argparse.ArgumentParser(description='Pattern automation CLI')
    parser.add_argument('--analyze', action='store_true', help='Analyze executions for patterns')
    parser.add_argument('--suggest', action='store_true', help='Generate pattern suggestions')
    parser.add_argument('--report', action='store_true', help='Generate weekly performance report')
    parser.add_argument('--db', default='core/state/pattern_metrics.db', help='Database path')
    
    args = parser.parse_args()
    
    # Get database path
    db_path = Path(args.db)
    if not db_path.exists():
        # Default to project root
        project_root = Path(__file__).parent.parent.parent.parent
        db_path = project_root / 'core' / 'state' / 'pipeline.db'
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        print("   Run database migration first: sqlite3 {db} < core/state/migrations/add_pattern_telemetry.sql")
        return 1
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    
    try:
        if args.analyze:
            print("🔍 Analyzing executions for patterns...")
            output_dir = Path(__file__).parent.parent / 'patterns' / 'drafts'
            result = analyze_executions(db_path, output_dir)
            print(f"✅ Processed {result['executions_processed']} executions")
            print(f"   Found {result['patterns_detected']} patterns")
            print(f"   Output: {result['output_dir']}")
        
        if args.suggest:
            print("💡 Generating pattern suggestions...")
            analyzer = PatternPerformanceAnalyzer(conn)
            candidates = analyzer._detect_manual_work()
            
            if candidates:
                print(f"\n📋 Found {len(candidates)} pattern candidates:\n")
                for c in candidates:
                    print(f"  • {c['operation_kind']}: {c['manual_count']} manual executions")
                    print(f"    → {c['suggestion']}\n")
            else:
                print("   No new pattern candidates detected.")
        
        if args.report:
            print("📊 Generating weekly performance report...")
            analyzer = PatternPerformanceAnalyzer(conn)
            report_file = analyzer.generate_weekly_report()
            print(f"✅ Report generated: {report_file}")
            
            # Also run anti-pattern detection
            print("\n⚠️  Checking for anti-patterns...")
            detector = AntiPatternDetector(conn)
            anti_patterns = detector.detect_anti_patterns()
            
            if anti_patterns:
                print(f"   Found {len(anti_patterns)} anti-patterns")
                for ap in anti_patterns:
                    print(f"   • {ap['name']}: {ap['occurrences']} occurrences")
            else:
                print("   No anti-patterns detected.")
        
        if not (args.analyze or args.suggest or args.report):
            parser.print_help()
            return 1
        
        return 0
    
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())
