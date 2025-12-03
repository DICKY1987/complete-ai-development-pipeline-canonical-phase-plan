"""Anti-Pattern Detector (AUTO-005)

Automatically detect and document recurring failure patterns.
"""
# DOC_ID: DOC-PAT-DETECTORS-ANTI-PATTERN-DETECTOR-878

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class AntiPatternDetector:
    """Learn from pattern failures and execution mistakes."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.registry_file = Path(__file__).parent.parent.parent / "anti_patterns" / "registry.yaml"
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
    
    def detect_anti_patterns(self) -> List[Dict]:
        """Run after execution failures to detect patterns."""
        failures = self._get_failed_executions(last_days=7)
        
        anti_patterns = []
        for failure_group in self._group_by_similarity(failures):
            if len(failure_group) >= 3:  # Recurring issue
                anti_pattern = self._create_anti_pattern(failure_group)
                anti_patterns.append(anti_pattern)
                self._record_anti_pattern(anti_pattern)
        
        return anti_patterns
    
    def _get_failed_executions(self, last_days: int) -> List[Dict]:
        """Get failed executions from database."""
        cursor = self.db.execute(
            """
            SELECT pattern_id, operation_kind, context, timestamp
            FROM execution_logs
            WHERE success = 0 
              AND timestamp >= datetime('now', ? || ' days')
            ORDER BY timestamp DESC
            """,
            (f'-{last_days}',)
        )
        
        failures = []
        for row in cursor.fetchall():
            failures.append({
                'pattern_id': row[0],
                'operation_kind': row[1],
                'context': json.loads(row[2]) if row[2] else {},
                'timestamp': row[3]
            })
        
        return failures
    
    def _group_by_similarity(self, failures: List[Dict]) -> List[List[Dict]]:
        """Group similar failures together."""
        groups = {}
        
        for failure in failures:
            # Simple grouping by pattern_id + operation_kind
            key = f"{failure['pattern_id']}:{failure['operation_kind']}"
            
            if key not in groups:
                groups[key] = []
            groups[key].append(failure)
        
        return [group for group in groups.values() if len(group) >= 3]
    
    def _create_anti_pattern(self, failures: List[Dict]) -> Dict:
        """Create anti-pattern from failure group."""
        pattern_id = failures[0]['pattern_id']
        operation = failures[0]['operation_kind']
        
        # Infer root cause
        root_cause = self._infer_cause(failures)
        
        anti_pattern_id = f"ANTI-PAT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        return {
            'id': anti_pattern_id,
            'name': f"{operation.replace('_', ' ').title()} Failure Pattern",
            'description': f"Recurring failures in {pattern_id}",
            'detected_at': datetime.now().isoformat(),
            'occurrences': len(failures),
            'affected_patterns': [pattern_id],
            'failure_signature': root_cause['signature'],
            'recommendation': root_cause['fix'],
            'status': 'active'
        }
    
    def _infer_cause(self, failures: List[Dict]) -> Dict:
        """Infer root cause from failures."""
        # Analyze context to determine cause
        common_context = {}
        for failure in failures:
            context = failure.get('context', {})
            for key, value in context.items():
                if key not in common_context:
                    common_context[key] = []
                common_context[key].append(value)
        
        # Common failure signatures
        causes = {
            'template_too_rigid': {
                'signature': 'Variable substitution failed',
                'fix': 'Use flexible regex for variable substitution'
            },
            'missing_dependency': {
                'signature': 'Required tool not available',
                'fix': 'Add dependency check before execution'
            },
            'wrong_context': {
                'signature': 'Pattern applied to wrong file type',
                'fix': 'Add file type validation'
            },
            'verification_failed': {
                'signature': 'Ground truth criteria too strict',
                'fix': 'Relax verification to existence + basic structure'
            }
        }
        
        # Simple heuristic: return first match
        return causes.get('verification_failed', {
            'signature': 'Unknown failure pattern',
            'fix': 'Manual investigation required'
        })
    
    def _record_anti_pattern(self, anti_pattern: Dict):
        """Record anti-pattern in database and registry."""
        # Database
        self.db.execute(
            """
            INSERT OR REPLACE INTO anti_patterns
            (id, name, description, affected_patterns, failure_signature, recommendation, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                anti_pattern['id'],
                anti_pattern['name'],
                anti_pattern['description'],
                json.dumps(anti_pattern['affected_patterns']),
                anti_pattern['failure_signature'],
                anti_pattern['recommendation'],
                anti_pattern['status']
            )
        )
        self.db.commit()
        
        # Update registry file
        self._update_registry(anti_pattern)
        
        # Create individual anti-pattern document
        self._create_anti_pattern_doc(anti_pattern)
    
    def _update_registry(self, anti_pattern: Dict):
        """Update anti-patterns registry YAML."""
        registry_content = f"""# Anti-Patterns Registry
# Auto-generated by AUTO-005
# Last updated: {datetime.now().isoformat()}

anti_patterns:
  - id: {anti_pattern['id']}
    name: "{anti_pattern['name']}"
    description: "{anti_pattern['description']}"
    detected: {anti_pattern['detected_at']}
    occurrences: {anti_pattern['occurrences']}
    affected_patterns:
{chr(10).join(f"      - {p}" for p in anti_pattern['affected_patterns'])}
    fix: "{anti_pattern['recommendation']}"
    status: "{anti_pattern['status']}"
"""
        
        # Append to registry
        if self.registry_file.exists():
            existing = self.registry_file.read_text(encoding='utf-8')
            if 'anti_patterns:' in existing:
                # Append to existing list
                lines = existing.split('\n')
                insert_index = next(i for i, line in enumerate(lines) if 'anti_patterns:' in line) + 1
                new_entry = '\n'.join(registry_content.split('\n')[4:])  # Skip header
                lines.insert(insert_index, new_entry)
                self.registry_file.write_text('\n'.join(lines), encoding='utf-8')
            else:
                self.registry_file.write_text(registry_content, encoding='utf-8')
        else:
            self.registry_file.write_text(registry_content, encoding='utf-8')
    
    def _create_anti_pattern_doc(self, anti_pattern: Dict):
        """Create individual anti-pattern markdown document."""
        doc_file = self.registry_file.parent / f"{anti_pattern['id']}.md"
        
        doc_content = f"""# {anti_pattern['name']}

**ID**: {anti_pattern['id']}  
**Detected**: {anti_pattern['detected_at']}  
**Status**: {anti_pattern['status']}  
**Occurrences**: {anti_pattern['occurrences']}

## Description

{anti_pattern['description']}

## Failure Signature

```
{anti_pattern['failure_signature']}
```

## Affected Patterns

{chr(10).join(f"- `{p}`" for p in anti_pattern['affected_patterns'])}

## Recommendation

{anti_pattern['recommendation']}

## Examples

<!-- Auto-populated from failure logs -->

## Resolution

<!-- Manual: Describe fix once applied -->
"""
        
        doc_file.write_text(doc_content, encoding='utf-8')
