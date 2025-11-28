"""Pattern Analyzer - Main coordinator for pattern-driven error detection.

This module provides the main entry point for running systematic
pattern-based analysis on code. It coordinates all pattern categories
and generates comprehensive reports.

Usage:
    from error.patterns import PatternAnalyzer
    
    analyzer = PatternAnalyzer()
    result = analyzer.analyze_file("path/to/file.py")
    
    # Or analyze specific patterns
    result = analyzer.analyze_file(
        "path/to/file.py",
        categories=[PatternCategory.BOUNDARY_VALUE, PatternCategory.ERROR_PATH]
    )
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .types import (
    ChecklistItem,
    ModuleChecklist,
    PatternCategory,
    PatternFinding,
    PatternResult,
    PatternSeverity,
)
from .boundary_patterns import scan_file_for_boundary_issues
from .state_transition import scan_file_for_state_issues
from .error_path import scan_file_for_error_path_issues
from .integration_seam import scan_file_for_integration_issues
from .resource_patterns import scan_file_for_resource_issues
from .temporal_patterns import scan_file_for_temporal_issues


# Default checklist items per category
DEFAULT_CHECKLIST = {
    "input_validation": [
        "All inputs validated before processing",
        "Type checking for all parameters",
        "Range/boundary checking",
        "Null/empty handling",
        "Sanitization of user input",
    ],
    "error_handling": [
        "All external calls wrapped in try/catch or error handling",
        "Specific error messages (not generic)",
        "Logging at appropriate levels",
        "Graceful degradation paths",
        "No silent failures",
    ],
    "state_management": [
        "Initialization validated",
        "State transitions are atomic",
        "Concurrent access protected",
        "Cleanup on all exit paths",
        "State consistency checks",
    ],
    "integration": [
        "Timeouts configured",
        "Retry logic implemented",
        "Circuit breakers for external services",
        "Data validation at boundaries",
        "Versioning handled",
    ],
    "resource_management": [
        "File handles closed properly",
        "Database connections released",
        "Memory cleanup implemented",
        "Thread/process limits set",
        "Cache eviction configured",
    ],
    "temporal": [
        "Timezone-aware datetime usage",
        "DST boundary handling",
        "Leap year handling",
        "Concurrent request handling",
        "Timeout race condition handling",
    ],
}


class PatternAnalyzer:
    """Main analyzer for pattern-driven error detection.
    
    Coordinates multiple pattern scanners to provide comprehensive
    analysis of code for potential bugs and issues.
    """
    
    def __init__(
        self,
        categories: Optional[List[PatternCategory]] = None,
        severity_threshold: PatternSeverity = PatternSeverity.INFO,
    ) -> None:
        """Initialize the pattern analyzer.
        
        Args:
            categories: Pattern categories to analyze (None = all)
            severity_threshold: Minimum severity to report
        """
        self._categories = categories or list(PatternCategory)
        self._severity_threshold = severity_threshold
        
        # Map categories to scanner functions
        self._scanners = {
            PatternCategory.BOUNDARY_VALUE: scan_file_for_boundary_issues,
            PatternCategory.STATE_TRANSITION: scan_file_for_state_issues,
            PatternCategory.ERROR_PATH: scan_file_for_error_path_issues,
            PatternCategory.INTEGRATION_SEAM: scan_file_for_integration_issues,
            PatternCategory.RESOURCE_EXHAUSTION: scan_file_for_resource_issues,
            PatternCategory.TEMPORAL: scan_file_for_temporal_issues,
        }
    
    def analyze_file(
        self,
        file_path: str | Path,
        categories: Optional[List[PatternCategory]] = None,
    ) -> PatternResult:
        """Analyze a single file for pattern issues.
        
        Args:
            file_path: Path to the Python file to analyze
            categories: Override categories to check (None = use instance default)
            
        Returns:
            PatternResult with all findings
        """
        file_path = Path(file_path)
        categories_to_check = categories or self._categories
        
        start_time = time.time()
        all_findings: List[PatternFinding] = []
        
        for category in categories_to_check:
            scanner = self._scanners.get(category)
            if scanner:
                findings = scanner(file_path)
                # Filter by severity threshold
                filtered = [
                    f for f in findings
                    if self._severity_meets_threshold(f.severity)
                ]
                all_findings.extend(filtered)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Build summary
        summary = self._build_summary(all_findings)
        
        return PatternResult(
            file_path=str(file_path),
            patterns_checked=categories_to_check,
            findings=all_findings,
            summary=summary,
            duration_ms=duration_ms,
        )
    
    def analyze_directory(
        self,
        dir_path: str | Path,
        recursive: bool = True,
        file_pattern: str = "*.py",
    ) -> List[PatternResult]:
        """Analyze all files in a directory.
        
        Args:
            dir_path: Path to the directory
            recursive: Whether to search recursively
            file_pattern: Glob pattern for files to analyze
            
        Returns:
            List of PatternResult for each file
        """
        dir_path = Path(dir_path)
        results: List[PatternResult] = []
        
        if recursive:
            files = list(dir_path.rglob(file_pattern))
        else:
            files = list(dir_path.glob(file_pattern))
        
        for file_path in files:
            # Skip test files and __pycache__
            if "__pycache__" in str(file_path):
                continue
            if "test_" in file_path.name and "test_runner" not in file_path.name:
                continue
            
            result = self.analyze_file(file_path)
            results.append(result)
        
        return results
    
    def generate_checklist(
        self,
        file_path: str | Path,
    ) -> ModuleChecklist:
        """Generate a validation checklist for a module.
        
        This creates a checklist based on the DEFAULT_CHECKLIST template
        and checks which items pass for the given file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            ModuleChecklist with all items and their status
        """
        file_path = Path(file_path)
        checklist = ModuleChecklist(module_path=str(file_path))
        
        # Run analysis to get findings
        result = self.analyze_file(file_path)
        
        # Map findings to checklist categories
        findings_by_category: Dict[str, List[PatternFinding]] = {
            "input_validation": [],
            "error_handling": [],
            "state_management": [],
            "integration": [],
            "resource_management": [],
            "temporal": [],
        }
        
        category_map = {
            PatternCategory.BOUNDARY_VALUE: "input_validation",
            PatternCategory.ERROR_PATH: "error_handling",
            PatternCategory.STATE_TRANSITION: "state_management",
            PatternCategory.INTEGRATION_SEAM: "integration",
            PatternCategory.RESOURCE_EXHAUSTION: "resource_management",
            PatternCategory.TEMPORAL: "temporal",
        }
        
        for finding in result.findings:
            checklist_cat = category_map.get(finding.pattern_category)
            if checklist_cat:
                findings_by_category[checklist_cat].append(finding)
        
        # Create checklist items
        for category, items in DEFAULT_CHECKLIST.items():
            category_findings = findings_by_category.get(category, [])
            
            for item in items:
                # Check if there are any findings that indicate this item fails
                has_issue = any(
                    self._item_matches_finding(item, f)
                    for f in category_findings
                )
                
                checklist.items.append(ChecklistItem(
                    category=category,
                    item=item,
                    is_checked=not has_issue,
                    evidence=self._get_evidence(item, category_findings) if has_issue else None,
                ))
        
        return checklist
    
    def generate_test_matrix(
        self,
        file_path: str | Path,
    ) -> Dict[str, Any]:
        """Generate a comprehensive test matrix for a file.
        
        This creates test case suggestions for all identified issues
        and patterns in the file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict containing test matrix with categories and cases
        """
        file_path = Path(file_path)
        result = self.analyze_file(file_path)
        
        matrix: Dict[str, Any] = {
            "file": str(file_path),
            "total_findings": len(result.findings),
            "categories": {},
        }
        
        for finding in result.findings:
            category = finding.pattern_category.value
            if category not in matrix["categories"]:
                matrix["categories"][category] = {
                    "findings": [],
                    "test_cases": [],
                }
            
            matrix["categories"][category]["findings"].append({
                "code": finding.code,
                "message": finding.message,
                "line": finding.line,
                "severity": finding.severity.value,
            })
            
            if finding.test_case:
                matrix["categories"][category]["test_cases"].append(finding.test_case)
        
        return matrix
    
    def _severity_meets_threshold(self, severity: PatternSeverity) -> bool:
        """Check if a severity meets the configured threshold."""
        severity_order = {
            PatternSeverity.INFO: 0,
            PatternSeverity.MINOR: 1,
            PatternSeverity.MAJOR: 2,
            PatternSeverity.CRITICAL: 3,
        }
        return severity_order[severity] >= severity_order[self._severity_threshold]
    
    def _build_summary(self, findings: List[PatternFinding]) -> Dict[str, Any]:
        """Build a summary of findings."""
        summary: Dict[str, Any] = {
            "total_findings": len(findings),
            "by_severity": {
                PatternSeverity.CRITICAL.value: 0,
                PatternSeverity.MAJOR.value: 0,
                PatternSeverity.MINOR.value: 0,
                PatternSeverity.INFO.value: 0,
            },
            "by_category": {},
            "has_critical": False,
            "has_major": False,
        }
        
        for finding in findings:
            summary["by_severity"][finding.severity.value] += 1
            
            cat = finding.pattern_category.value
            if cat not in summary["by_category"]:
                summary["by_category"][cat] = 0
            summary["by_category"][cat] += 1
            
            if finding.severity == PatternSeverity.CRITICAL:
                summary["has_critical"] = True
            if finding.severity == PatternSeverity.MAJOR:
                summary["has_major"] = True
        
        return summary
    
    def _item_matches_finding(self, item: str, finding: PatternFinding) -> bool:
        """Check if a checklist item is related to a finding."""
        item_lower = item.lower()
        
        # Match based on keywords
        keywords = {
            "validated": ["BVA", "validation"],
            "type checking": ["BVA", "type"],
            "boundary": ["BVA", "boundary"],
            "null": ["null", "none", "empty"],
            "sanitization": ["xss", "injection", "sanitiz"],
            "try/catch": ["EPC", "exception"],
            "error messages": ["error", "message"],
            "logging": ["log", "logging"],
            "silent": ["silent", "EPC"],
            "state": ["STG", "state"],
            "atomic": ["atomic", "concurrent"],
            "cleanup": ["cleanup", "release"],
            "timeout": ["timeout", "ISA"],
            "retry": ["retry", "ISA"],
            "circuit": ["circuit", "ISA"],
            "file handles": ["RES", "file"],
            "connection": ["RES", "connection"],
            "memory": ["RES", "memory"],
            "thread": ["RES", "thread"],
            "cache": ["RES", "cache"],
            "timezone": ["TMP", "timezone"],
            "dst": ["TMP", "dst"],
            "leap": ["TMP", "leap"],
            "concurrent": ["concurrent", "race"],
        }
        
        for keyword, patterns in keywords.items():
            if keyword in item_lower:
                for pattern in patterns:
                    if pattern in finding.code or pattern.lower() in finding.message.lower():
                        return True
        
        return False
    
    def _get_evidence(self, item: str, findings: List[PatternFinding]) -> str:
        """Get evidence for why a checklist item fails."""
        matching = [f for f in findings if self._item_matches_finding(item, f)]
        if matching:
            finding = matching[0]
            return f"Line {finding.line}: {finding.message}" if finding.line else finding.message
        return "Potential issue detected"


def analyze_module(
    module_path: str | Path,
    categories: Optional[List[PatternCategory]] = None,
) -> PatternResult:
    """Convenience function to analyze a module.
    
    Args:
        module_path: Path to the module to analyze
        categories: Optional list of categories to check
        
    Returns:
        PatternResult with findings
    """
    analyzer = PatternAnalyzer(categories=categories)
    return analyzer.analyze_file(module_path)


def generate_gap_report(
    module_path: str | Path,
) -> str:
    """Generate a markdown gap report for a module.
    
    Args:
        module_path: Path to the module to analyze
        
    Returns:
        Markdown-formatted gap report
    """
    analyzer = PatternAnalyzer()
    result = analyzer.analyze_file(module_path)
    checklist = analyzer.generate_checklist(module_path)
    
    report_lines = [
        f"# Pattern Analysis Gap Report",
        f"",
        f"**File**: `{module_path}`",
        f"**Analysis Time**: {result.duration_ms}ms",
        f"",
        f"## Summary",
        f"",
        f"- **Total Findings**: {len(result.findings)}",
        f"- **Critical**: {result.summary.get('by_severity', {}).get('critical', 0)}",
        f"- **Major**: {result.summary.get('by_severity', {}).get('major', 0)}",
        f"- **Minor**: {result.summary.get('by_severity', {}).get('minor', 0)}",
        f"",
        f"## Checklist Results",
        f"",
        f"**Pass Rate**: {checklist.pass_rate:.1f}% ({checklist.passing_count}/{checklist.total_count})",
        f"",
    ]
    
    # Group checklist by category
    for category in DEFAULT_CHECKLIST.keys():
        items = checklist.get_by_category(category)
        if items:
            report_lines.append(f"### {category.replace('_', ' ').title()}")
            report_lines.append("")
            for item in items:
                status = "✅" if item.is_checked else "❌"
                report_lines.append(f"- [{status}] {item.item}")
                if item.evidence:
                    report_lines.append(f"  - *{item.evidence}*")
            report_lines.append("")
    
    # Findings by category
    if result.findings:
        report_lines.append("## Detailed Findings")
        report_lines.append("")
        
        for category, findings in result.findings_by_category.items():
            report_lines.append(f"### {category.value.replace('_', ' ').title()}")
            report_lines.append("")
            for finding in findings:
                sev_emoji = {
                    PatternSeverity.CRITICAL: "🔴",
                    PatternSeverity.MAJOR: "🟠",
                    PatternSeverity.MINOR: "🟡",
                    PatternSeverity.INFO: "🔵",
                }.get(finding.severity, "⚪")
                
                line_info = f" (line {finding.line})" if finding.line else ""
                report_lines.append(f"- {sev_emoji} **{finding.code}**{line_info}: {finding.message}")
                if finding.suggested_fix:
                    # Truncate long suggestions
                    fix = finding.suggested_fix.strip()
                    if len(fix) > 100:
                        fix = fix[:100] + "..."
                    report_lines.append(f"  - Fix: {fix}")
            report_lines.append("")
    
    return "\n".join(report_lines)
