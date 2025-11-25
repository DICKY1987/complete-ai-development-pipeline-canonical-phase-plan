"""Error Recovery Pattern Learner (AUTO-003)

Learn from successful error resolutions and create self-healing patterns.
Integrates with error/engine/error_engine.py.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ErrorRecoveryPatternLearner:
    """Extract patterns from successful error recoveries."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.min_occurrences = 3  # Need 3+ successful fixes to learn
        self.auto_apply_threshold = 0.9  # 90% success rate for auto-apply
    
    def on_error_resolved(self, error_record: Dict, resolution: Dict):
        """Called when error fixed successfully."""
        error_type = error_record.get('type', 'unknown')
        error_signature = error_record.get('signature', '')
        resolution_steps = resolution.get('steps', [])
        success = resolution.get('success', False)
        
        # Record in database
        self._record_resolution(error_type, error_signature, resolution_steps, success)
        
        # Check if we can create a pattern
        if success:
            self._check_for_healing_pattern(error_type, error_signature)
    
    def _record_resolution(self, error_type: str, error_signature: str, 
                          resolution_steps: List[str], success: bool):
        """Record error resolution in database."""
        cursor = self.db.execute(
            """
            SELECT id, occurrences, successful_resolutions, failed_resolutions
            FROM error_patterns
            WHERE error_signature = ?
            """,
            (error_signature,)
        )
        
        row = cursor.fetchone()
        
        if row:
            # Update existing
            occurrences = row[1] + 1
            successful = row[2] + (1 if success else 0)
            failed = row[3] + (0 if success else 1)
            success_rate = successful / occurrences
            auto_apply = success_rate >= self.auto_apply_threshold
            
            self.db.execute(
                """
                UPDATE error_patterns
                SET occurrences = ?, successful_resolutions = ?, failed_resolutions = ?,
                    success_rate = ?, auto_apply = ?, resolution_steps = ?, updated_at = ?
                WHERE id = ?
                """,
                (occurrences, successful, failed, success_rate, auto_apply,
                 json.dumps(resolution_steps), datetime.now(), row[0])
            )
        else:
            # Insert new
            self.db.execute(
                """
                INSERT INTO error_patterns
                (error_type, error_signature, resolution_steps, occurrences,
                 successful_resolutions, failed_resolutions, success_rate, auto_apply)
                VALUES (?, ?, ?, 1, ?, ?, ?, ?)
                """,
                (error_type, error_signature, json.dumps(resolution_steps),
                 1 if success else 0, 0 if success else 1,
                 1.0 if success else 0.0, False)
            )
        
        self.db.commit()
    
    def _check_for_healing_pattern(self, error_type: str, error_signature: str):
        """Check if we have enough data to create auto-healing pattern."""
        cursor = self.db.execute(
            """
            SELECT occurrences, successful_resolutions, success_rate, resolution_steps, auto_apply
            FROM error_patterns
            WHERE error_signature = ?
            """,
            (error_signature,)
        )
        
        row = cursor.fetchone()
        if not row:
            return
        
        occurrences, successful, success_rate, resolution_steps, auto_apply = row
        
        # Need 3+ successful resolutions
        if successful >= self.min_occurrences and success_rate >= 0.8:
            self._create_healing_pattern(
                error_type, error_signature, 
                json.loads(resolution_steps), 
                success_rate, occurrences, auto_apply
            )
    
    def _create_healing_pattern(self, error_type: str, error_signature: str,
                                resolution_steps: List[str], success_rate: float,
                                learned_from: int, auto_apply: bool):
        """Create auto-healing pattern file."""
        pattern_id = f"AUTO-HEAL-{error_type.upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create pattern directory
        pattern_dir = Path(__file__).parent.parent.parent / "specs" / "self_heal"
        pattern_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate YAML
        yaml_content = f"""# Auto-Generated Self-Healing Pattern
# Created: {datetime.now().isoformat()}
# Confidence: {success_rate:.2%}
# Learned from: {learned_from} successful resolutions

pattern_id: {pattern_id}
name: Auto-heal {error_type.replace('_', ' ').title()}
version: "1.0.0"
category: error_recovery
status: {'approved' if auto_apply else 'draft'}
auto_generated: true

error_detection:
  type: {error_type}
  signature: |
    {error_signature[:200]}

resolution:
  auto_apply: {str(auto_apply).lower()}
  confidence: {success_rate:.2f}
  steps:
{chr(10).join(f"    - {step}" for step in resolution_steps)}

metadata:
  learned_from_cases: {learned_from}
  success_rate: {success_rate:.2%}
  auto_apply_threshold: {self.auto_apply_threshold:.2%}
  created_at: "{datetime.now().isoformat()}"
"""
        
        pattern_file = pattern_dir / f"{pattern_id}.yaml"
        pattern_file.write_text(yaml_content, encoding='utf-8')
        
        print(f"\n✅ Auto-healing pattern created: {pattern_id}")
        print(f"   Success rate: {success_rate:.2%}")
        print(f"   Auto-apply: {auto_apply}")
        print(f"   File: {pattern_file}")
    
    def get_resolution_suggestion(self, error_signature: str) -> Optional[Dict]:
        """Get suggested resolution for an error."""
        cursor = self.db.execute(
            """
            SELECT error_type, resolution_steps, success_rate, auto_apply
            FROM error_patterns
            WHERE error_signature = ? OR error_signature LIKE ?
            ORDER BY success_rate DESC
            LIMIT 1
            """,
            (error_signature, f"%{error_signature[:50]}%")
        )
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            'error_type': row[0],
            'resolution_steps': json.loads(row[1]),
            'success_rate': row[2],
            'auto_apply': bool(row[3])
        }
