#!/usr/bin/env python
"""
Analyze pytest JSON report and generate test triage summary.

PATTERN: EXEC-002 (Module Enhancement)
DOC_ID: DOC-SCRIPT-ANALYZE-TEST-RESULTS-001

Purpose: Quick Win #4 - Automated test failure analysis
Time: 4 hours | Saves: 8h/month (no manual test log review)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class TestResultAnalyzer:
    """Analyze pytest JSON report and generate actionable insights."""

    def __init__(self, report_path: Path):
        self.report_path = report_path
        self.report_data = self._load_report()
        
    def _load_report(self) -> Dict[str, Any]:
        """Load JSON report."""
        if not self.report_path.exists():
            raise FileNotFoundError(f"Report not found: {self.report_path}")
        
        with open(self.report_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze(self) -> Dict[str, Any]:
        """Generate comprehensive analysis."""
        summary = self.report_data.get('summary', {})
        tests = self.report_data.get('tests', [])
        
        # Categorize tests
        passed = [t for t in tests if t.get('outcome') == 'passed']
        failed = [t for t in tests if t.get('outcome') == 'failed']
        skipped = [t for t in tests if t.get('outcome') == 'skipped']
        errors = [t for t in tests if t.get('outcome') == 'error']
        
        # Categorize failures by type
        failure_categories = self._categorize_failures(failed)
        
        # Find flaky tests (if we have historical data)
        # For now, just track recent failures
        
        analysis = {
            'summary': {
                'total': summary.get('total', 0),
                'passed': summary.get('passed', 0),
                'failed': summary.get('failed', 0),
                'skipped': summary.get('skipped', 0),
                'errors': len(errors),
                'duration': summary.get('duration', 0),
                'success_rate': self._calculate_success_rate(summary),
            },
            'failures': {
                'count': len(failed),
                'by_category': failure_categories,
                'details': self._extract_failure_details(failed),
            },
            'errors': {
                'count': len(errors),
                'details': self._extract_failure_details(errors),
            },
            'skipped': {
                'count': len(skipped),
                'reasons': self._extract_skip_reasons(skipped),
            },
            'slowest_tests': self._find_slowest_tests(tests, limit=10),
            'recommendations': self._generate_recommendations(failed, errors),
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        return analysis
    
    def _calculate_success_rate(self, summary: Dict) -> float:
        """Calculate test success rate."""
        total = summary.get('total', 0)
        if total == 0:
            return 0.0
        passed = summary.get('passed', 0)
        return round((passed / total) * 100, 2)
    
    def _categorize_failures(self, failed_tests: List[Dict]) -> Dict[str, int]:
        """Categorize failures by error type."""
        categories = {
            'assertion': 0,
            'timeout': 0,
            'import_error': 0,
            'attribute_error': 0,
            'type_error': 0,
            'other': 0,
        }
        
        for test in failed_tests:
            call = test.get('call', {})
            longrepr = str(call.get('longrepr', '')).lower()
            
            if 'assertionerror' in longrepr or 'assert' in longrepr:
                categories['assertion'] += 1
            elif 'timeout' in longrepr:
                categories['timeout'] += 1
            elif 'importerror' in longrepr or 'modulenotfounderror' in longrepr:
                categories['import_error'] += 1
            elif 'attributeerror' in longrepr:
                categories['attribute_error'] += 1
            elif 'typeerror' in longrepr:
                categories['type_error'] += 1
            else:
                categories['other'] += 1
        
        return {k: v for k, v in categories.items() if v > 0}
    
    def _extract_failure_details(self, failed_tests: List[Dict]) -> List[Dict]:
        """Extract key details from failed tests."""
        details = []
        
        for test in failed_tests[:20]:  # Limit to first 20 failures
            call = test.get('call', {})
            details.append({
                'test_id': test.get('nodeid', 'unknown'),
                'duration': test.get('duration', 0),
                'error_type': self._extract_error_type(call),
                'error_message': self._extract_error_message(call),
                'file': self._extract_file_path(test.get('nodeid', '')),
            })
        
        return details
    
    def _extract_error_type(self, call_info: Dict) -> str:
        """Extract error type from call info."""
        longrepr = str(call_info.get('longrepr', ''))
        
        # Look for exception type
        lines = longrepr.split('\n')
        for line in lines:
            if 'Error' in line or 'Exception' in line:
                parts = line.split(':')
                if parts:
                    return parts[0].strip()
        
        return 'Unknown'
    
    def _extract_error_message(self, call_info: Dict) -> str:
        """Extract first line of error message."""
        longrepr = str(call_info.get('longrepr', ''))
        lines = [l.strip() for l in longrepr.split('\n') if l.strip()]
        
        # Return last non-empty line (usually the actual error)
        return lines[-1] if lines else 'No error message'
    
    def _extract_file_path(self, nodeid: str) -> str:
        """Extract file path from test node ID."""
        if '::' in nodeid:
            return nodeid.split('::')[0]
        return nodeid
    
    def _extract_skip_reasons(self, skipped_tests: List[Dict]) -> Dict[str, int]:
        """Extract and count skip reasons."""
        reasons = {}
        
        for test in skipped_tests:
            setup = test.get('setup', {})
            longrepr = str(setup.get('longrepr', ''))
            
            # Extract reason (usually after "Skipped: ")
            if 'Skipped:' in longrepr:
                reason = longrepr.split('Skipped:')[1].strip().split('\n')[0]
            else:
                reason = 'Unknown'
            
            reasons[reason] = reasons.get(reason, 0) + 1
        
        return reasons
    
    def _find_slowest_tests(self, tests: List[Dict], limit: int = 10) -> List[Dict]:
        """Find slowest running tests."""
        sorted_tests = sorted(
            tests,
            key=lambda t: t.get('duration', 0),
            reverse=True
        )
        
        return [
            {
                'test_id': t.get('nodeid', 'unknown'),
                'duration': round(t.get('duration', 0), 3),
                'outcome': t.get('outcome', 'unknown'),
            }
            for t in sorted_tests[:limit]
        ]
    
    def _generate_recommendations(self, failed: List[Dict], errors: List[Dict]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if len(failed) > 10:
            recommendations.append(
                f"⚠️ High failure rate ({len(failed)} tests) - Consider running subset first"
            )
        
        if len(errors) > 0:
            recommendations.append(
                f"🔴 {len(errors)} test errors (not failures) - Check test setup/fixtures"
            )
        
        # Check for common patterns
        failure_types = self._categorize_failures(failed)
        
        if failure_types.get('import_error', 0) > 0:
            recommendations.append(
                "📦 Import errors detected - Verify dependencies installed"
            )
        
        if failure_types.get('timeout', 0) > 0:
            recommendations.append(
                "⏱️ Timeout failures detected - Consider increasing timeout or optimizing"
            )
        
        if not recommendations:
            if len(failed) == 0:
                recommendations.append("✅ All tests passed - Great job!")
            else:
                recommendations.append(
                    f"🔍 Review {len(failed)} failures individually"
                )
        
        return recommendations
    
    def print_summary(self):
        """Print human-readable summary to console."""
        analysis = self.analyze()
        
        print("=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        print()
        
        summary = analysis['summary']
        print(f"Total Tests:    {summary['total']}")
        print(f"✅ Passed:      {summary['passed']}")
        print(f"❌ Failed:      {summary['failed']}")
        print(f"⏭️  Skipped:     {summary['skipped']}")
        print(f"🔴 Errors:      {summary['errors']}")
        print(f"⏱️  Duration:    {summary['duration']:.2f}s")
        print(f"📊 Success Rate: {summary['success_rate']}%")
        print()
        
        if analysis['failures']['count'] > 0:
            print("─" * 70)
            print("FAILURES BY CATEGORY")
            print("─" * 70)
            for category, count in analysis['failures']['by_category'].items():
                print(f"  {category}: {count}")
            print()
            
            print("─" * 70)
            print("TOP FAILURES")
            print("─" * 70)
            for i, failure in enumerate(analysis['failures']['details'][:5], 1):
                print(f"{i}. {failure['test_id']}")
                print(f"   Error: {failure['error_type']}")
                print(f"   {failure['error_message'][:100]}")
                print()
        
        if analysis['slowest_tests']:
            print("─" * 70)
            print("SLOWEST TESTS (Top 5)")
            print("─" * 70)
            for i, test in enumerate(analysis['slowest_tests'][:5], 1):
                print(f"{i}. {test['test_id']} - {test['duration']}s")
            print()
        
        print("─" * 70)
        print("RECOMMENDATIONS")
        print("─" * 70)
        for rec in analysis['recommendations']:
            print(f"  {rec}")
        print()
        
        print("=" * 70)
    
    def save_triage_report(self, output_path: Path):
        """Save detailed triage report."""
        analysis = self.analyze()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"✅ Triage report saved: {output_path}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_test_results.py <json_report_path> [output_path]")
        print("\nExample:")
        print("  python analyze_test_results.py .state/test_results.json")
        print("  python analyze_test_results.py .state/test_results.json .state/triage.json")
        return 1
    
    report_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('.state/test_triage.json')
    
    try:
        analyzer = TestResultAnalyzer(report_path)
        analyzer.print_summary()
        analyzer.save_triage_report(output_path)
        
        # Exit with failure code if tests failed
        analysis = analyzer.analyze()
        if analysis['summary']['failed'] > 0 or analysis['summary']['errors'] > 0:
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error analyzing test results: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
