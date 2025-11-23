#!/usr/bin/env python
"""
Extract Patterns from CLI Logs
Main CLI for pattern extraction workstream WS-PATTERN-01
"""

import argparse
import sys
from pathlib import Path
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pattern_extraction.parsers.copilot_parser import CopilotParser
from pattern_extraction.detectors.parallel_detector import ParallelDetector
from pattern_extraction.generators.yaml_template_generator import YAMLTemplateGenerator


def main():
    parser = argparse.ArgumentParser(
        description='Extract execution patterns from CLI logs and generate YAML templates'
    )
    parser.add_argument(
        '--copilot-logs',
        default=str(Path.home() / '.copilot' / 'session-state'),
        help='Path to Copilot session-state logs'
    )
    parser.add_argument(
        '--output',
        default='templates/patterns',
        help='Output directory for generated templates'
    )
    parser.add_argument(
        '--min-frequency',
        type=int,
        default=3,
        help='Minimum pattern frequency to include'
    )
    parser.add_argument(
        '--max-patterns',
        type=int,
        default=50,
        help='Maximum number of patterns to extract'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Pattern Extraction from CLI Logs (WS-PATTERN-01)")
    print("=" * 60)
    
    # Step 1: Parse logs
    print(f"\n[1/4] Parsing Copilot logs from {args.copilot_logs}...")
    copilot_parser = CopilotParser()
    
    copilot_logs = Path(args.copilot_logs)
    if not copilot_logs.exists():
        print(f"❌ Error: Log path not found: {copilot_logs}")
        return 1
    
    sessions = copilot_parser.parse_logs(str(copilot_logs))
    print(f"  ✅ Parsed {len(sessions)} sessions")
    
    if not sessions:
        print("❌ No sessions found in logs")
        return 1
    
    # Step 2: Detect parallel patterns
    print(f"\n[2/4] Detecting parallel execution patterns...")
    parallel_detector = ParallelDetector()
    parallel_patterns = parallel_detector.detect_patterns(sessions)
    
    # Filter by frequency
    parallel_patterns = [p for p in parallel_patterns if p.frequency >= args.min_frequency]
    parallel_patterns = parallel_patterns[:args.max_patterns]
    
    print(f"  ✅ Found {len(parallel_patterns)} parallel patterns (min frequency: {args.min_frequency})")
    
    # Step 3: Generate YAML templates
    print(f"\n[3/4] Generating YAML templates...")
    generator = YAMLTemplateGenerator()
    output_dir = Path(args.output)
    
    generated_files = []
    for pattern in parallel_patterns:
        try:
            filepath = generator.save_template(pattern, output_dir)
            generated_files.append(filepath)
            print(f"  ✅ {filepath.name} (freq={pattern.frequency}, savings={pattern.time_savings_percent:.0f}%)")
        except Exception as e:
            print(f"  ❌ Error generating template for {pattern.pattern_id}: {e}")
    
    # Step 4: Summary report
    print(f"\n[4/4] Summary")
    print("=" * 60)
    print(f"Sessions analyzed: {len(sessions)}")
    print(f"Patterns detected: {len(parallel_patterns)}")
    print(f"Templates generated: {len(generated_files)}")
    print(f"Output directory: {output_dir.absolute()}")
    
    if parallel_patterns:
        print(f"\nTop 5 patterns by frequency:")
        for i, pattern in enumerate(parallel_patterns[:5], 1):
            tools = ' + '.join(pattern.tool_sequence)
            print(f"  {i}. {tools}")
            print(f"     Frequency: {pattern.frequency} uses")
            print(f"     Time savings: {pattern.time_savings_percent:.0f}%")
            print(f"     Avg duration: {pattern.avg_duration_seconds:.2f}s")
    
    print(f"\n✅ Pattern extraction complete!")
    print(f"   Generated {len(generated_files)} YAML templates")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
