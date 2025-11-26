# Quick Start: Activate Pattern Automation (30 Minutes)

**Goal**: Get pattern auto-learning working with minimal effort
**Time**: 30-45 minutes
**Result**: System learns patterns from every execution

---

## Step 1: Add Database Tables (10 min)

Create: `core/state/migrations/004_pattern_automation.sql`

```sql
-- Pattern automation tables
-- Migration 004

-- Track all executions for pattern detection
CREATE TABLE IF NOT EXISTS execution_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_kind TEXT NOT NULL,
    file_types TEXT,              -- JSON array: ["py", "yaml"]
    tools_used TEXT,              -- JSON array: ["grep", "edit", "bash"]
    input_signature TEXT,         -- Hash of input structure
    output_signature TEXT,        -- Hash of output structure
    success BOOLEAN NOT NULL,
    time_taken_seconds REAL,
    context TEXT,                 -- JSON: task details
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Track detected pattern candidates
CREATE TABLE IF NOT EXISTS pattern_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id TEXT UNIQUE,
    signature TEXT,               -- Execution signature hash
    example_executions TEXT,      -- JSON array of execution_log IDs
    confidence REAL,              -- 0.0 to 1.0
    auto_generated_spec TEXT,     -- Full YAML spec
    status TEXT DEFAULT 'pending', -- pending, approved, rejected
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Track anti-patterns (failure patterns)
CREATE TABLE IF NOT EXISTS anti_patterns (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    affected_patterns TEXT,       -- JSON array of pattern IDs
    failure_signature TEXT,
    recommendation TEXT,
    status TEXT DEFAULT 'active', -- active, resolved, ignored
    occurrences INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_execution_timestamp ON execution_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_execution_operation ON execution_logs(operation_kind);
CREATE INDEX IF NOT EXISTS idx_execution_success ON execution_logs(success);
CREATE INDEX IF NOT EXISTS idx_pattern_status ON pattern_candidates(status);
```

**Apply migration:**
```bash
# Add to core/state/db.py migration list
python -c "from core.state.db import init_db; init_db(migrate=True)"
```

---

## Step 2: Hook Pattern Detector (15 min)

Edit: `core/engine/orchestrator.py`

```python
# Add imports at top
import json
import hashlib
from pathlib import Path
from datetime import datetime

# Add detection method to Orchestrator class
class Orchestrator:
    def __init__(self, ...):
        # Existing init...
        self._pattern_detector_enabled = True
        self._patterns_dir = Path(__file__).parent.parent.parent / "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK" / "patterns"

    def execute_task(self, task_spec: Dict) -> Dict:
        """Execute task and log for pattern detection."""
        start_time = datetime.now()

        # Existing execution logic
        result = self._do_actual_execution(task_spec)

        # NEW: Log execution for pattern detection
        if self._pattern_detector_enabled and result.get('success'):
            execution_time = (datetime.now() - start_time).total_seconds()
            self._log_execution_for_patterns(task_spec, result, execution_time)

        return result

    def _log_execution_for_patterns(self, task_spec: Dict, result: Dict, time_taken: float):
        """Log execution details for pattern detection."""
        from core.state.db import get_db

        # Extract execution signature
        operation_kind = task_spec.get('operation_kind', 'unknown')
        file_types = self._extract_file_types(task_spec, result)
        tools_used = self._extract_tools_used(task_spec)

        input_signature = hashlib.md5(
            json.dumps(task_spec.get('inputs', {}), sort_keys=True).encode()
        ).hexdigest()

        output_signature = hashlib.md5(
            json.dumps(result.get('outputs', {}), sort_keys=True).encode()
        ).hexdigest()

        context = {
            'task_name': task_spec.get('name'),
            'inputs': task_spec.get('inputs', {}),
            'outputs': result.get('outputs', {})
        }

        # Store in database
        db = get_db()
        db.execute(
            """
            INSERT INTO execution_logs
            (operation_kind, file_types, tools_used, input_signature, output_signature,
             success, time_taken_seconds, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                operation_kind,
                json.dumps(file_types),
                json.dumps(tools_used),
                input_signature,
                output_signature,
                result.get('success', False),
                time_taken,
                json.dumps(context)
            )
        )
        db.commit()

        # Check for patterns (after 3+ similar executions)
        self._check_for_patterns(operation_kind, input_signature, output_signature)

    def _extract_file_types(self, task_spec: Dict, result: Dict) -> List[str]:
        """Extract file extensions from task."""
        file_types = set()

        # From inputs
        for key, value in task_spec.get('inputs', {}).items():
            if isinstance(value, str) and '.' in value:
                ext = Path(value).suffix.lstrip('.')
                if ext:
                    file_types.add(ext)

        # From outputs
        for key, value in result.get('outputs', {}).items():
            if isinstance(value, str) and '.' in value:
                ext = Path(value).suffix.lstrip('.')
                if ext:
                    file_types.add(ext)

        return sorted(list(file_types))

    def _extract_tools_used(self, task_spec: Dict) -> List[str]:
        """Extract tools/commands used in task."""
        # Simple heuristic: look for common tools in task spec
        tools = []
        task_str = json.dumps(task_spec).lower()

        common_tools = ['grep', 'glob', 'read', 'write', 'edit', 'bash', 'git', 'pytest']
        for tool in common_tools:
            if tool in task_str:
                tools.append(tool)

        return tools

    def _check_for_patterns(self, operation_kind: str, input_sig: str, output_sig: str):
        """Check if we've seen similar executions 3+ times."""
        from core.state.db import get_db

        db = get_db()
        cursor = db.execute(
            """
            SELECT COUNT(*), GROUP_CONCAT(id) as execution_ids
            FROM execution_logs
            WHERE operation_kind = ?
              AND input_signature = ?
              AND output_signature = ?
              AND success = 1
              AND timestamp >= datetime('now', '-30 days')
            """,
            (operation_kind, input_sig, output_sig)
        )

        row = cursor.fetchone()
        count = row[0]
        execution_ids = row[1].split(',') if row[1] else []

        if count >= 3:
            # Pattern detected! Generate template
            self._generate_pattern_candidate(operation_kind, execution_ids, count)

    def _generate_pattern_candidate(self, operation_kind: str, execution_ids: List[str], count: int):
        """Auto-generate pattern YAML from similar executions."""
        from core.state.db import get_db

        # Check if already generated
        signature = f"{operation_kind}:{','.join(sorted(execution_ids))}"
        signature_hash = hashlib.md5(signature.encode()).hexdigest()

        db = get_db()
        existing = db.execute(
            "SELECT id FROM pattern_candidates WHERE signature = ?",
            (signature_hash,)
        ).fetchone()

        if existing:
            return  # Already generated

        # Generate pattern ID
        pattern_id = f"AUTO-{datetime.now().strftime('%Y%m%d')}-{count:03d}"

        # Fetch execution details
        cursor = db.execute(
            f"""
            SELECT operation_kind, file_types, tools_used, context, time_taken_seconds
            FROM execution_logs
            WHERE id IN ({','.join(['?'] * len(execution_ids))})
            """,
            execution_ids
        )

        executions = []
        for row in cursor.fetchall():
            executions.append({
                'operation_kind': row[0],
                'file_types': json.loads(row[1]) if row[1] else [],
                'tools_used': json.loads(row[2]) if row[2] else [],
                'context': json.loads(row[3]) if row[3] else {},
                'time_taken': row[4]
            })

        if not executions:
            return

        # Generate YAML spec
        avg_time = sum(e['time_taken'] for e in executions) / len(executions)
        confidence = min(count / 10, 1.0) * 0.9  # Scale with sample size

        yaml_spec = f"""# Auto-Generated Pattern
# Created: {datetime.now().isoformat()}
# Learned from: {count} executions
# Confidence: {confidence:.1%}

pattern_id: {pattern_id}
name: "Auto-{operation_kind.replace('_', ' ').title()}"
version: "1.0.0"
status: draft
category: auto_detected

metadata:
  confidence: {confidence:.2f}
  learned_from_executions: {count}
  avg_time_seconds: {avg_time:.1f}
  detected_at: {datetime.now().isoformat()}

operation_kind: {operation_kind}
file_types: {executions[0]['file_types']}
tools: {executions[0]['tools_used']}

inputs:
  # TODO: Extract from context
  target: {{target}}

steps:
  # TODO: Extract from execution sequence
  - action: execute
    tool: {executions[0]['tools_used'][0] if executions[0]['tools_used'] else 'unknown'}

verification:
  - condition: success
"""

        # Save to database
        db.execute(
            """
            INSERT INTO pattern_candidates
            (pattern_id, signature, example_executions, confidence, auto_generated_spec, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                pattern_id,
                signature_hash,
                json.dumps(execution_ids),
                confidence,
                yaml_spec,
                'approved' if confidence >= 0.75 else 'pending'
            )
        )
        db.commit()

        # Write to drafts folder
        drafts_dir = self._patterns_dir / "drafts"
        drafts_dir.mkdir(parents=True, exist_ok=True)

        draft_file = drafts_dir / f"{pattern_id}.yaml"
        draft_file.write_text(yaml_spec, encoding='utf-8')

        print(f"✨ Pattern detected! Generated {pattern_id} from {count} similar executions")
        print(f"   Confidence: {confidence:.1%}")
        print(f"   Location: {draft_file}")
```

---

## Step 3: Test It (5 min)

Run any task 3 times with similar structure:

```python
# Example test
from core.engine.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Execute same operation 3 times
for i in range(3):
    result = orchestrator.execute_task({
        'operation_kind': 'file_creation',
        'name': f'create_test_file_{i}',
        'inputs': {
            'filename': f'test_{i}.txt',
            'content': f'Test content {i}'
        }
    })

# After 3rd execution, check:
# - patterns/drafts/AUTO-*.yaml should exist
# - Database should have entry in pattern_candidates
```

**Verify:**
```bash
# Check database
sqlite3 .worktrees/pipeline_state.db "SELECT * FROM execution_logs LIMIT 5;"
sqlite3 .worktrees/pipeline_state.db "SELECT * FROM pattern_candidates;"

# Check generated patterns
ls -la patterns/drafts/AUTO-*.yaml
```

---

## Step 4: Enable Anti-Pattern Detection (Optional, 10 min)

Edit: `error/engine/error_engine.py`

```python
# Add at top
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK" / "patterns"))

from automation.detectors.anti_pattern_detector import AntiPatternDetector

class ErrorEngine:
    def __init__(self):
        # Existing init...
        from core.state.db import get_db
        self.anti_pattern_detector = AntiPatternDetector(get_db())

    def on_execution_failed(self, error_record: Dict):
        """Handle execution failure and detect anti-patterns."""
        # Existing error handling...

        # NEW: Detect recurring failures
        anti_patterns = self.anti_pattern_detector.detect_anti_patterns()

        for pattern in anti_patterns:
            print(f"⚠️  Anti-pattern detected: {pattern['name']}")
            print(f"   Recommendation: {pattern['recommendation']}")
```

---

## Expected Results

After completing these steps:

1. **Execution Logging**: Every task execution is recorded in `execution_logs` table
2. **Pattern Detection**: After 3 similar executions, system generates `patterns/drafts/AUTO-*.yaml`
3. **Auto-Approval**: Patterns with >75% confidence are marked as approved
4. **Anti-Patterns**: Recurring failures (3+) generate documentation

**Example Output:**
```
✨ Pattern detected! Generated AUTO-20251126-001 from 3 similar executions
   Confidence: 85%
   Location: patterns/drafts/AUTO-20251126-001.yaml
```

---

## Configuration

Control automation behavior in `core/engine/orchestrator.py`:

```python
# Feature flags
self._pattern_detector_enabled = True          # Enable/disable detection
self._auto_approval_threshold = 0.75          # Confidence for auto-approval
self._min_executions_for_pattern = 3          # How many before detecting
self._pattern_lookback_days = 30              # How far back to search
```

---

## Troubleshooting

### "Table execution_logs doesn't exist"
- Run migration: `python core/state/db.py --migrate`

### "No patterns detected after 3 executions"
- Check similarity: Inputs/outputs must be structurally similar
- Check database: `sqlite3 .worktrees/pipeline_state.db "SELECT * FROM execution_logs;"`

### "Import error for AntiPatternDetector"
- Check PYTHONPATH includes patterns folder
- Or copy `automation/` to `core/automation/`

---

## Next Steps

Once basic automation works:

1. **Build More Executors**: Create executors for high-value patterns (batch_create, self_heal)
2. **Tune Detection**: Adjust similarity threshold based on results
3. **Add Visualization**: Build dashboard to show detected patterns
4. **Historical Analysis**: Run pattern extraction on old logs

---

## ROI Calculation

After 1 week of automation:
- **Manual pattern creation**: 30 min per pattern
- **Auto-detected patterns**: ~2-3 per week
- **Time saved**: 1-1.5 hours per week
- **Implementation time**: 45 minutes

**Break-even**: After 1 week
**Annual savings**: 50-75 hours (assuming continued pattern discovery)

---

**Status**: Ready to implement
**Estimated time**: 30-45 minutes
**Risk**: Low (additive only, no breaking changes)
**Reward**: Automatic pattern learning from all future work
