"""Automated test failure classification and triage."""
DOC_ID: DOC-CORE-TESTING-AUTO-TRIAGE-852

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern


class FailureCategory(Enum):
    """Categories of test failures."""
    IMPORT_ERROR = "import_error"
    SYNTAX_ERROR = "syntax_error"
    ASSERTION_ERROR = "assertion_error"
    TIMEOUT = "timeout"
    KNOWN_FLAKY = "known_flaky"
    RESOURCE_ERROR = "resource_error"
    TYPE_ERROR = "type_error"
    ATTRIBUTE_ERROR = "attribute_error"
    UNKNOWN = "unknown"


@dataclass
class TriageResult:
    """Result of triaging a test failure."""
    
    category: FailureCategory
    auto_fixable: bool
    recommended_action: str
    confidence: float
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'category': self.category.value,
            'auto_fixable': self.auto_fixable,
            'recommended_action': self.recommended_action,
            'confidence': self.confidence,
            'details': self.details
        }


class TestTriage:
    """Automated test failure classification and triage system."""
    
    # Patterns for detecting failure types
    PATTERNS = {
        FailureCategory.IMPORT_ERROR: [
            r'ImportError: No module named',
            r'ModuleNotFoundError:',
            r'cannot import name'
        ],
        FailureCategory.SYNTAX_ERROR: [
            r'SyntaxError:',
            r'invalid syntax'
        ],
        FailureCategory.ASSERTION_ERROR: [
            r'AssertionError:',
            r'assert .* == .*'
        ],
        FailureCategory.TIMEOUT: [
            r'TimeoutError',
            r'timeout',
            r'timed out'
        ],
        FailureCategory.TYPE_ERROR: [
            r'TypeError:',
            r'expected .* got .*'
        ],
        FailureCategory.ATTRIBUTE_ERROR: [
            r'AttributeError:',
            r"object has no attribute"
        ],
        FailureCategory.RESOURCE_ERROR: [
            r'MemoryError',
            r'OSError:',
            r'PermissionError'
        ]
    }
    
    def __init__(
        self,
        known_flaky_tests: Optional[List[str]] = None,
        triage_log: Optional[Path] = None
    ):
        """Initialize test triage system.
        
        Args:
            known_flaky_tests: List of known flaky test patterns
            triage_log: Path to triage log file
        """
        self.known_flaky = known_flaky_tests or []
        self.triage_log = triage_log or Path(".state/test_triage.jsonl")
        self.triage_log.parent.mkdir(parents=True, exist_ok=True)
        self._compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[FailureCategory, List[Pattern]]:
        """Compile regex patterns for faster matching."""
        compiled = {}
        for category, patterns in self.PATTERNS.items():
            compiled[category] = [re.compile(p, re.IGNORECASE) for p in patterns]
        return compiled
    
    def classify_failure(
        self,
        test_output: str,
        test_name: Optional[str] = None
    ) -> TriageResult:
        """Classify a test failure and recommend action.
        
        Args:
            test_output: Test output/error message
            test_name: Optional test name for flaky detection
            
        Returns:
            TriageResult with category and recommended action
        """
        if test_name and self._is_known_flaky(test_name):
            return TriageResult(
                category=FailureCategory.KNOWN_FLAKY,
                auto_fixable=False,
                recommended_action="skip_and_log",
                confidence=1.0,
                details={'test_name': test_name}
            )
        
        for category, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(test_output):
                    return self._create_result(category, test_output, test_name)
        
        return TriageResult(
            category=FailureCategory.UNKNOWN,
            auto_fixable=False,
            recommended_action="manual_review",
            confidence=0.0,
            details={'output_snippet': test_output[:500]}
        )
    
    def _is_known_flaky(self, test_name: str) -> bool:
        """Check if test is known to be flaky."""
        return any(pattern in test_name for pattern in self.known_flaky)
    
    def _create_result(
        self,
        category: FailureCategory,
        output: str,
        test_name: Optional[str]
    ) -> TriageResult:
        """Create triage result based on category."""
        fixable_categories = {
            FailureCategory.IMPORT_ERROR,
            FailureCategory.SYNTAX_ERROR
        }
        
        auto_fixable = category in fixable_categories
        
        action_map = {
            FailureCategory.IMPORT_ERROR: "create_error_recovery_task",
            FailureCategory.SYNTAX_ERROR: "create_error_recovery_task",
            FailureCategory.ASSERTION_ERROR: "analyze_logic_bug",
            FailureCategory.TIMEOUT: "increase_timeout_or_optimize",
            FailureCategory.TYPE_ERROR: "create_error_recovery_task",
            FailureCategory.ATTRIBUTE_ERROR: "create_error_recovery_task",
            FailureCategory.RESOURCE_ERROR: "check_resources",
            FailureCategory.KNOWN_FLAKY: "skip_and_log",
            FailureCategory.UNKNOWN: "manual_review"
        }
        
        confidence_map = {
            FailureCategory.IMPORT_ERROR: 0.95,
            FailureCategory.SYNTAX_ERROR: 0.95,
            FailureCategory.ASSERTION_ERROR: 0.80,
            FailureCategory.TIMEOUT: 0.70,
            FailureCategory.TYPE_ERROR: 0.85,
            FailureCategory.ATTRIBUTE_ERROR: 0.85,
            FailureCategory.RESOURCE_ERROR: 0.75,
            FailureCategory.KNOWN_FLAKY: 1.0,
            FailureCategory.UNKNOWN: 0.0
        }
        
        details = {
            'output_snippet': output[:500],
            'test_name': test_name
        }
        
        if category == FailureCategory.IMPORT_ERROR:
            details['missing_module'] = self._extract_missing_module(output)
        
        return TriageResult(
            category=category,
            auto_fixable=auto_fixable,
            recommended_action=action_map.get(category, "manual_review"),
            confidence=confidence_map.get(category, 0.5),
            details=details
        )
    
    def _extract_missing_module(self, output: str) -> Optional[str]:
        """Extract missing module name from ImportError."""
        patterns = [
            r"No module named '([^']+)'",
            r"No module named ([^\s]+)",
            r"ModuleNotFoundError: No module named '([^']+)'"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output)
            if match:
                return match.group(1)
        
        return None
    
    def triage_batch(
        self,
        test_results: List[Dict[str, Any]]
    ) -> List[TriageResult]:
        """Triage multiple test failures.
        
        Args:
            test_results: List of test result dictionaries with 'name' and 'output' keys
            
        Returns:
            List of TriageResult objects
        """
        results = []
        for test_result in test_results:
            triage_result = self.classify_failure(
                test_output=test_result.get('output', ''),
                test_name=test_result.get('name')
            )
            results.append(triage_result)
            self._record_triage(test_result, triage_result)
        
        return results
    
    def _record_triage(
        self,
        test_result: Dict[str, Any],
        triage_result: TriageResult
    ) -> None:
        """Record triage decision to log."""
        record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'test_name': test_result.get('name'),
            'triage': triage_result.to_dict()
        }
        
        with open(self.triage_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')
    
    def get_auto_fixable_failures(
        self,
        test_results: List[Dict[str, Any]]
    ) -> List[TriageResult]:
        """Get only auto-fixable failures from test results.
        
        Args:
            test_results: List of test result dictionaries
            
        Returns:
            List of auto-fixable TriageResult objects
        """
        all_triaged = self.triage_batch(test_results)
        return [t for t in all_triaged if t.auto_fixable]
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics from triage log.
        
        Returns:
            Dictionary with triage statistics
        """
        if not self.triage_log.exists():
            return {'total': 0}
        
        category_counts = {}
        auto_fixable_count = 0
        total = 0
        
        with open(self.triage_log, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                triage = record['triage']
                category = triage['category']
                
                category_counts[category] = category_counts.get(category, 0) + 1
                if triage['auto_fixable']:
                    auto_fixable_count += 1
                total += 1
        
        return {
            'total': total,
            'auto_fixable': auto_fixable_count,
            'by_category': category_counts,
            'auto_fixable_percentage': (auto_fixable_count / total * 100) if total > 0 else 0
        }
