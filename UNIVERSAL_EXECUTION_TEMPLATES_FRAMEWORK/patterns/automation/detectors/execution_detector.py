"""Execution Pattern Detector (AUTO-001)

Automatically detect repetitive execution patterns from telemetry data.
Generates pattern candidates after detecting 3+ similar executions.
"""
DOC_ID: DOC-PAT-DETECTORS-EXECUTION-DETECTOR-881

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ExecutionSignature:
    """Fingerprint of an execution for pattern matching."""
    operation_kind: str
    file_types: List[str]
    tools_used: List[str]
    input_structure_hash: str
    output_structure_hash: str
    
    def similarity(self, other: 'ExecutionSignature') -> float:
        """Calculate similarity score (0.0 to 1.0)."""
        if self.operation_kind != other.operation_kind:
            return 0.0
        
        # File type overlap
        self_files = set(self.file_types)
        other_files = set(other.file_types)
        file_similarity = len(self_files & other_files) / max(len(self_files | other_files), 1)
        
        # Tool sequence similarity
        self_tools = set(self.tools_used)
        other_tools = set(other.tools_used)
        tool_similarity = len(self_tools & other_tools) / max(len(self_tools | other_tools), 1)
        
        # Structure similarity (exact match for now)
        structure_match = 1.0 if (self.input_structure_hash == other.input_structure_hash and 
                                   self.output_structure_hash == other.output_structure_hash) else 0.5
        
        # Weighted average
        return 0.3 * file_similarity + 0.3 * tool_similarity + 0.4 * structure_match


class ExecutionPatternDetector:
    """Automatically detect repetitive execution patterns."""
    
    def __init__(self, db_connection, similarity_threshold: float = 0.75):
        self.db = db_connection
        self.similarity_threshold = similarity_threshold
        self.pattern_dir = Path(__file__).parent.parent.parent / "drafts"
        self.pattern_dir.mkdir(parents=True, exist_ok=True)
    
    def on_execution_complete(self, execution_record: Dict):
        """Hook called after each execution completes."""
        signature = self._extract_signature(execution_record)
        
        # Find similar executions
        similar = self._find_similar_executions(signature)
        
        if len(similar) >= 3:
            # Generate pattern candidate
            pattern = self._synthesize_pattern(similar + [execution_record])
            if pattern['confidence'] >= 0.75:  # Aggressive mode threshold
                self._create_pattern_draft(pattern)
    
    def _extract_signature(self, record: Dict) -> ExecutionSignature:
        """Extract execution fingerprint."""
        # Hash input/output structures for comparison
        input_hash = hashlib.md5(json.dumps(record.get('inputs', {}), sort_keys=True).encode()).hexdigest()
        output_hash = hashlib.md5(json.dumps(record.get('outputs', {}), sort_keys=True).encode()).hexdigest()
        
        return ExecutionSignature(
            operation_kind=record.get('operation_kind', 'unknown'),
            file_types=record.get('file_types', []),
            tools_used=record.get('tools_used', []),
            input_structure_hash=input_hash,
            output_structure_hash=output_hash
        )
    
    def _find_similar_executions(self, signature: ExecutionSignature, days_back: int = 30) -> List[Dict]:
        """Find similar executions from recent history."""
        cutoff = datetime.now() - timedelta(days=days_back)
        
        cursor = self.db.execute(
            """
            SELECT id, operation_kind, file_types, tools_used, input_signature, output_signature, 
                   success, time_taken_seconds, context, timestamp
            FROM execution_logs
            WHERE timestamp >= ? AND success = 1
            ORDER BY timestamp DESC
            """,
            (cutoff,)
        )
        
        similar = []
        for row in cursor.fetchall():
            record_sig = ExecutionSignature(
                operation_kind=row[1],
                file_types=json.loads(row[2]) if row[2] else [],
                tools_used=json.loads(row[3]) if row[3] else [],
                input_structure_hash=row[4] or '',
                output_structure_hash=row[5] or ''
            )
            
            if signature.similarity(record_sig) >= self.similarity_threshold:
                similar.append({
                    'id': row[0],
                    'operation_kind': row[1],
                    'file_types': json.loads(row[2]) if row[2] else [],
                    'tools_used': json.loads(row[3]) if row[3] else [],
                    'success': bool(row[6]),
                    'time_taken_seconds': row[7],
                    'context': json.loads(row[8]) if row[8] else {},
                    'timestamp': row[9]
                })
        
        return similar
    
    def _synthesize_pattern(self, executions: List[Dict]) -> Dict:
        """Generate pattern from similar executions."""
        # Extract invariants (same across all)
        invariants = self._extract_invariants(executions)
        
        # Extract variables (different per execution)
        variables = self._extract_variables(executions)
        
        # Calculate confidence
        confidence = self._calculate_confidence(executions)
        
        # Generate pattern ID
        pattern_id = f"AUTO-{datetime.now().strftime('%Y%m%d')}-{len(list(self.pattern_dir.glob('AUTO-*.yaml'))) + 1:03d}"
        
        # Estimate time savings
        avg_time = sum(e['time_taken_seconds'] for e in executions) / len(executions)
        time_savings = self._estimate_savings(avg_time)
        
        return {
            'pattern_id': pattern_id,
            'name': self._infer_pattern_name(executions),
            'operation_kind': invariants.get('operation_kind'),
            'invariants': invariants,
            'variables': variables,
            'template': self._generate_template(invariants, variables),
            'confidence': confidence,
            'time_savings_estimate': time_savings,
            'learned_from': len(executions),
            'example_execution_ids': [e['id'] for e in executions]
        }
    
    def _extract_invariants(self, executions: List[Dict]) -> Dict:
        """Extract what's the same across all executions."""
        if not executions:
            return {}
        
        # Start with first execution
        first = executions[0]
        invariants = {
            'operation_kind': first['operation_kind'],
            'tools_used': first['tools_used']
        }
        
        # Remove anything that varies
        for exec in executions[1:]:
            if exec['operation_kind'] != invariants['operation_kind']:
                invariants.pop('operation_kind', None)
            if exec['tools_used'] != invariants['tools_used']:
                invariants.pop('tools_used', None)
        
        return invariants
    
    def _extract_variables(self, executions: List[Dict]) -> Dict:
        """Extract what varies between executions."""
        variables = {}
        
        # Collect unique values for each field
        file_types_set = set()
        for exec in executions:
            file_types_set.update(exec.get('file_types', []))
        
        if file_types_set:
            variables['file_types'] = {
                'type': 'list',
                'examples': list(file_types_set)[:5]
            }
        
        # Extract from context
        context_keys = set()
        for exec in executions:
            context_keys.update(exec.get('context', {}).keys())
        
        if context_keys:
            variables['context_params'] = {
                'type': 'dict',
                'keys': list(context_keys)
            }
        
        return variables
    
    def _generate_template(self, invariants: Dict, variables: Dict) -> str:
        """Generate pattern template structure."""
        template = f"""# Auto-Generated Pattern Template
# Detected from {len(variables.get('examples', []))} similar executions

operation_kind: {invariants.get('operation_kind', 'unknown')}

inputs:
"""
        
        for var_name, var_info in variables.items():
            template += f"  {var_name}: {{{var_name}}}  # {var_info.get('type', 'string')}\n"
        
        template += "\nsteps:\n"
        if 'tools_used' in invariants:
            for tool in invariants['tools_used']:
                template += f"  - tool: {tool}\n"
        
        return template
    
    def _calculate_confidence(self, executions: List[Dict]) -> float:
        """Calculate confidence score for pattern."""
        # Success rate
        successes = sum(1 for e in executions if e.get('success', False))
        success_rate = successes / len(executions)
        
        # Sample size (more executions = higher confidence)
        sample_score = min(len(executions) / 10, 1.0)
        
        # Similarity (how consistent are the executions)
        # For now, assume high if we got this far
        similarity_score = 0.85
        
        return 0.4 * success_rate + 0.3 * sample_score + 0.3 * similarity_score
    
    def _estimate_savings(self, avg_time_seconds: float) -> str:
        """Estimate time savings from using pattern."""
        # Assume pattern reduces time by 60% (template vs manual)
        manual_time = avg_time_seconds / 0.4  # If pattern is 40% of manual time
        savings_seconds = manual_time - avg_time_seconds
        savings_minutes = savings_seconds / 60
        
        return f"{savings_minutes:.0f} minutes per execution"
    
    def _infer_pattern_name(self, executions: List[Dict]) -> str:
        """Infer descriptive name from executions."""
        operation = executions[0].get('operation_kind', 'unknown')
        file_types = executions[0].get('file_types', [])
        
        if file_types:
            return f"Auto-{operation.replace('_', ' ').title()} for {', '.join(file_types[:2])}"
        return f"Auto-{operation.replace('_', ' ').title()}"
    
    def _create_pattern_draft(self, pattern: Dict):
        """Create draft pattern file and record in database."""
        # Generate YAML
        yaml_content = f"""# Auto-Generated Pattern
# Created: {datetime.now().isoformat()}
# Confidence: {pattern['confidence']:.2%}
# Learned from: {pattern['learned_from']} executions

pattern_id: {pattern['pattern_id']}
name: "{pattern['name']}"
version: "1.0.0"
status: draft
category: auto_detected
auto_generated: true

metadata:
  confidence: {pattern['confidence']:.2f}
  learned_from_executions: {pattern['learned_from']}
  estimated_time_savings: "{pattern['time_savings_estimate']}"
  example_execution_ids: {pattern['example_execution_ids']}

{pattern['template']}
"""
        
        # Write to drafts/
        draft_file = self.pattern_dir / f"{pattern['pattern_id']}.yaml"
        draft_file.write_text(yaml_content, encoding='utf-8')
        
        # Record in database
        signature = hashlib.md5(json.dumps(pattern['invariants'], sort_keys=True).encode()).hexdigest()
        
        cursor = self.db.execute(
            """
            INSERT INTO pattern_candidates 
            (signature, example_executions, confidence, auto_generated_spec, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                signature,
                json.dumps(pattern['example_execution_ids']),
                pattern['confidence'],
                yaml_content,
                'pending' if pattern['confidence'] < 0.75 else 'approved'  # Aggressive mode
            )
        )
        self.db.commit()
        
        # If confidence >= 0.75, auto-approve (aggressive mode)
        if pattern['confidence'] >= 0.75:
            self._auto_approve_pattern(pattern, cursor.lastrowid)
    
    def _auto_approve_pattern(self, pattern: Dict, candidate_id: int):
        """Auto-approve high-confidence patterns (aggressive mode)."""
        # Move from drafts/ to specs/
        draft_file = self.pattern_dir / f"{pattern['pattern_id']}.yaml"
        specs_dir = self.pattern_dir.parent / "specs" / "auto_approved"
        specs_dir.mkdir(parents=True, exist_ok=True)
        
        approved_file = specs_dir / f"{pattern['pattern_id']}.yaml"
        
        # Update YAML with approval note
        content = draft_file.read_text(encoding='utf-8')
        content = content.replace('status: draft', 'status: approved')
        content += f"\n# Auto-approved at {datetime.now().isoformat()} (confidence >= 75%)\n"
        
        approved_file.write_text(content, encoding='utf-8')
        
        # Update database
        self.db.execute(
            "UPDATE pattern_candidates SET status = 'approved' WHERE id = ?",
            (candidate_id,)
        )
        self.db.commit()
        
        print(f"[auto-approve] pattern: {pattern['pattern_id']} (confidence: {pattern['confidence']:.2%})")


def analyze_executions(db_path: Path, output_dir: Path):
    """Analyze recent executions for patterns."""
    import sqlite3
    
    conn = sqlite3.connect(db_path)
    detector = ExecutionPatternDetector(conn, similarity_threshold=0.75)
    
    # Get recent executions
    cursor = conn.execute(
        """
        SELECT id, operation_kind, file_types, tools_used, input_signature, output_signature,
               success, time_taken_seconds, context
        FROM execution_logs
        WHERE timestamp >= datetime('now', '-30 days')
        ORDER BY timestamp DESC
        """
    )
    
    processed = 0
    patterns_found = 0
    
    for row in cursor.fetchall():
        record = {
            'id': row[0],
            'operation_kind': row[1],
            'file_types': json.loads(row[2]) if row[2] else [],
            'tools_used': json.loads(row[3]) if row[3] else [],
            'inputs': {'signature': row[4]},
            'outputs': {'signature': row[5]},
            'success': bool(row[6]),
            'time_taken_seconds': row[7],
            'context': json.loads(row[8]) if row[8] else {}
        }
        
        detector.on_execution_complete(record)
        processed += 1
    
    patterns_found = len(list(detector.pattern_dir.glob("AUTO-*.yaml")))
    
    conn.close()
    
    return {
        'executions_processed': processed,
        'patterns_detected': patterns_found,
        'output_dir': str(detector.pattern_dir)
    }
