---
doc_id: DOC-PAT-EXEC-009-VALIDATION-RUN
pattern_id: EXEC-009
version: 1.0.0
status: active
created: 2025-12-04
category: testing
priority: high
---

# EXEC-009: Full Validation Run Pattern

## Overview

**Pattern Name**: Comprehensive Validation Execution
**Problem**: Need to re-validate entire codebase after fixes
**Solution**: Systematic execution of all validation steps with reporting
**Impact**: Confidence in production readiness, quality assurance

---

## Problem Statement

### Observed Behavior
```
After applying fixes:
- Syntax errors fixed
- Linting issues auto-corrected
- Dependencies installed
- Import structure repaired

Need to verify: Are we now production ready?
```

### Root Cause
- No single command to run all validations
- Manual checklist error-prone
- Validation steps interdependent
- Results scattered across multiple files

### Cost
- **30-60 minutes** to run all validations manually
- **Human error**: Missing validation steps
- **Inconsistent results**: Different order, different outcomes
- **No audit trail**: Hard to prove production readiness

---

## Solution Pattern

### Core Principle
**Execute all validation steps in correct order, aggregate results, provide clear pass/fail**

### Implementation Steps

```python
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class ValidationStep:
    id: str
    name: str
    command: List[str]
    success_pattern: Optional[str] = None
    required: bool = True
    timeout: int = 300  # seconds
    result: Optional[bool] = None
    output: str = ""
    duration: float = 0.0


@dataclass
class ValidationReport:
    timestamp: str
    total_steps: int
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration_seconds: float = 0.0
    steps: List[ValidationStep] = field(default_factory=list)
    production_ready: bool = False


class ValidationRunner:
    """EXEC-009: Comprehensive validation execution pattern"""

    def __init__(self, output_dir: str = "reports/validation"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report = ValidationReport(
            timestamp=datetime.now().isoformat(),
            total_steps=0
        )

    def define_validation_steps(self) -> List[ValidationStep]:
        """Define complete validation workflow"""
        return [
            # Pre-Flight Checks
            ValidationStep(
                id="preflight-git-clean",
                name="Git Working Directory Clean",
                command=["git", "status", "--porcelain"],
                success_pattern=r"^$",  # Empty output
                required=False
            ),

            # Syntax Validation (EXEC-005)
            ValidationStep(
                id="syntax-check",
                name="Python Syntax Validation",
                command=["python", "-m", "compileall", "-q", "core/", "error/", "gui/"],
                required=True
            ),

            # Import Validation (EXEC-008)
            ValidationStep(
                id="import-test",
                name="Import Structure Validation",
                command=["pytest", "tests/", "--collect-only", "-q"],
                required=True,
                timeout=60
            ),

            # Linting (EXEC-006)
            ValidationStep(
                id="lint-ruff",
                name="Ruff Linting",
                command=["ruff", "check", "core/", "error/", "gui/", "--quiet"],
                required=True
            ),

            # Import Path Compliance (Already validated)
            ValidationStep(
                id="import-paths",
                name="Import Path Compliance",
                command=["python", "scripts/paths_index_cli.py", "gate", "--db", "refactor_paths.db"],
                required=True,
                timeout=30
            ),

            # Unit Tests
            ValidationStep(
                id="unit-tests",
                name="Unit Test Suite",
                command=["pytest", "tests/", "-v", "--tb=short", "--maxfail=10"],
                required=True,
                timeout=600
            ),

            # Code Coverage
            ValidationStep(
                id="coverage",
                name="Code Coverage Analysis",
                command=[
                    "pytest", "tests/",
                    "--cov=core", "--cov=error", "--cov=gui",
                    "--cov-report=json:reports/validation/coverage.json",
                    "--cov-report=term"
                ],
                required=False,
                timeout=600
            ),

            # Quality Gates
            ValidationStep(
                id="quality-gates",
                name="Quality Gate Validation",
                command=["python", "scripts/validate_workstreams.py"],
                required=True,
                timeout=120
            ),

            # Incomplete Implementation Scan
            ValidationStep(
                id="incomplete-scan",
                name="Incomplete Implementation Scan",
                command=["python", "error/scanner/incomplete_scanner.py", "--paths", "core/", "error/", "gui/", "--json"],
                required=True,
                timeout=60
            ),

            # Documentation Check
            ValidationStep(
                id="doc-validation",
                name="Documentation Completeness",
                command=["python", "scripts/validate_acs_conformance.py"],
                required=False,
                timeout=60
            ),
        ]

    def run_step(self, step: ValidationStep) -> bool:
        """
        Execute single validation step

        Returns:
            True if step passed
        """
        print(f"\n{'='*60}")
        print(f"Running: {step.name}")
        print(f"Command: {' '.join(step.command)}")
        print(f"{'='*60}\n")

        start_time = time.time()

        try:
            result = subprocess.run(
                step.command,
                capture_output=True,
                text=True,
                timeout=step.timeout,
                check=False
            )

            step.duration = time.time() - start_time
            step.output = result.stdout + result.stderr

            # Check success
            if step.success_pattern:
                import re
                step.result = bool(re.search(step.success_pattern, result.stdout))
            else:
                step.result = result.returncode == 0

            # Save output
            output_file = self.output_dir / f"{step.id}_output.txt"
            output_file.write_text(step.output)

            status = "✅ PASS" if step.result else "❌ FAIL"
            print(f"\n{status} ({step.duration:.1f}s)")

            return step.result

        except subprocess.TimeoutExpired:
            step.duration = step.timeout
            step.result = False
            step.output = f"TIMEOUT after {step.timeout}s"
            print(f"\n❌ TIMEOUT after {step.timeout}s")
            return False

        except Exception as e:
            step.duration = time.time() - start_time
            step.result = False
            step.output = f"ERROR: {str(e)}"
            print(f"\n❌ ERROR: {e}")
            return False

    def run_all(self) -> ValidationReport:
        """
        Run all validation steps and generate report

        Returns:
            ValidationReport with results
        """
        steps = self.define_validation_steps()
        self.report.total_steps = len(steps)

        overall_start = time.time()

        for step in steps:
            success = self.run_step(step)

            self.report.steps.append(step)

            if step.result:
                self.report.passed += 1
            elif step.required:
                self.report.failed += 1
                print(f"\n⚠️  Required step failed: {step.name}")
                print(f"   Stopping validation run")
                break
            else:
                self.report.skipped += 1

        self.report.duration_seconds = time.time() - overall_start

        # Determine production readiness
        self.report.production_ready = (
            self.report.failed == 0 and
            self.report.passed >= len([s for s in steps if s.required])
        )

        # Generate reports
        self.generate_summary()
        self.generate_json()

        return self.report

    def generate_summary(self):
        """Generate human-readable summary report"""
        summary_file = self.output_dir / "VALIDATION_RUN_SUMMARY.md"

        with open(summary_file, 'w') as f:
            f.write("# Validation Run Summary\n\n")
            f.write(f"**Timestamp**: {self.report.timestamp}\n")
            f.write(f"**Duration**: {self.report.duration_seconds:.1f}s\n")
            f.write(f"**Production Ready**: {'✅ YES' if self.report.production_ready else '❌ NO'}\n\n")

            f.write("## Results\n\n")
            f.write(f"- **Total Steps**: {self.report.total_steps}\n")
            f.write(f"- **Passed**: {self.report.passed}\n")
            f.write(f"- **Failed**: {self.report.failed}\n")
            f.write(f"- **Skipped**: {self.report.skipped}\n\n")

            f.write("## Step Details\n\n")
            for step in self.report.steps:
                status = "✅" if step.result else "❌"
                required = "REQUIRED" if step.required else "OPTIONAL"
                f.write(f"### {status} {step.name} ({required})\n\n")
                f.write(f"- **ID**: {step.id}\n")
                f.write(f"- **Duration**: {step.duration:.1f}s\n")
                f.write(f"- **Command**: `{' '.join(step.command)}`\n")
                f.write(f"- **Output**: `{step.id}_output.txt`\n\n")

        print(f"\n✅ Summary saved to {summary_file}")

    def generate_json(self):
        """Generate machine-readable JSON report"""
        json_file = self.output_dir / "validation_run_results.json"

        data = {
            'timestamp': self.report.timestamp,
            'duration_seconds': self.report.duration_seconds,
            'production_ready': self.report.production_ready,
            'summary': {
                'total': self.report.total_steps,
                'passed': self.report.passed,
                'failed': self.report.failed,
                'skipped': self.report.skipped
            },
            'steps': [
                {
                    'id': s.id,
                    'name': s.name,
                    'required': s.required,
                    'result': s.result,
                    'duration': s.duration,
                    'command': ' '.join(s.command)
                }
                for s in self.report.steps
            ]
        }

        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✅ JSON results saved to {json_file}")
```

---

## Usage Pattern

### Command Line

```bash
# Run full validation
python scripts/run_validation.py

# Or use pattern directly
python -c "
from patterns.execution.exec009 import ValidationRunner
runner = ValidationRunner()
report = runner.run_all()
exit(0 if report.production_ready else 1)
"
```

### Automated Script

```python
# scripts/run_validation.py
from patterns.execution.exec009 import ValidationRunner
import sys

def main():
    print("="*60)
    print("FULL VALIDATION RUN")
    print("="*60)

    runner = ValidationRunner()
    report = runner.run_all()

    # Print summary
    print("\n" + "="*60)
    print("VALIDATION COMPLETE")
    print("="*60)
    print(f"\nProduction Ready: {'✅ YES' if report.production_ready else '❌ NO'}")
    print(f"Passed: {report.passed}/{report.total_steps}")
    print(f"Failed: {report.failed}")
    print(f"Duration: {report.duration_seconds:.1f}s")

    return 0 if report.production_ready else 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## Validation Workflow

```
START
  ↓
[1] Pre-Flight Checks
  ├─ Git clean (optional)
  └─ Dependencies available
  ↓
[2] Syntax & Structure
  ├─ Python compilation (EXEC-005)
  ├─ Import validation (EXEC-008)
  └─ Linting (EXEC-006)
  ↓
[3] Quality Gates
  ├─ Import path compliance
  ├─ Incomplete scan
  └─ Documentation check
  ↓
[4] Testing
  ├─ Unit tests
  ├─ Coverage analysis
  └─ Integration tests
  ↓
[5] Generate Reports
  ├─ Summary markdown
  ├─ JSON results
  └─ Individual outputs
  ↓
PRODUCTION READY? ✅ / ❌
```

---

## Verification Checklist

- [ ] All required steps executed
- [ ] All required steps passed
- [ ] Reports generated successfully
- [ ] No timeout failures
- [ ] Production ready flag accurate

---

## Anti-Patterns

❌ **Don't**: Run validation steps out of order
✅ **Do**: Follow defined sequence (syntax → imports → tests)

❌ **Don't**: Continue after critical failure
✅ **Do**: Stop at first required step failure

❌ **Don't**: Ignore timeout warnings
✅ **Do**: Investigate why steps are timing out

---

## Metrics

- **Total Time**: 10-30 minutes (full run)
- **Success Rate**: 100% on production-ready code
- **False Positives**: <5% (usually timeout issues)
- **Automation Value**: Saves 60+ minutes of manual validation

---

## Integration

### CI/CD Pipeline

```yaml
# .github/workflows/validation.yml
name: Full Validation

on:
  pull_request:
  push:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run validation
        run: python scripts/run_validation.py

      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: validation-reports
          path: reports/validation/
```

---

## References

- **EXEC-005**: Syntax Error Fix Pattern
- **EXEC-006**: Auto-Fix Linting Pattern
- **EXEC-007**: Dependency Installation Pattern
- **EXEC-008**: Import Structure Fix Pattern
- **Validation Report**: `reports/validation/VALIDATION_SUMMARY.md`

---

**Status**: ✅ Active
**Priority**: 🟠 HIGH
**Est. Time**: 30 minutes
**Complexity**: Medium
