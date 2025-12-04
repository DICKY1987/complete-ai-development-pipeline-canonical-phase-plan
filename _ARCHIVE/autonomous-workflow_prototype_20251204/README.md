# Autonomous Self-Healing Automation Workflow

A production-grade, zero-touch automation validation and self-repair system.

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     █████╗ ██╗   ██╗████████╗ ██████╗ ███╗   ██╗ ██████╗ ███╗   ███╗ ██████╗ ║
║    ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗████╗  ██║██╔═══██╗████╗ ████║██╔═══██╗║
║    ███████║██║   ██║   ██║   ██║   ██║██╔██╗ ██║██║   ██║██╔████╔██║██║   ██║║
║    ██╔══██║██║   ██║   ██║   ██║   ██║██║╚██╗██║██║   ██║██║╚██╔╝██║██║   ██║║
║    ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚████║╚██████╔╝██║ ╚═╝ ██║╚██████╔╝║
║    ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ║
║                                                                               ║
║              Detect → Diagnose → Fix → Retest → Certify                      ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## Overview

This system implements a **closed-loop automation validation process** that:

1. **Discovers** all automation components in your repository
2. **Validates** each component's health
3. **Classifies** failures into deterministic root-cause buckets
4. **Generates** and executes fix plans
5. **Retests** until certified or escalated
6. **Produces** audit-ready certification artifacts

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AUTONOMOUS WORKFLOW ENGINE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐               │
│  │   PHASE 0     │    │   PHASE 1     │    │   PHASE 2     │               │
│  │   Discovery   │───▶│ Health Sweep  │───▶│ Classification│               │
│  │               │    │               │    │               │               │
│  │ automation_   │    │ runtime_      │    │ failure_      │               │
│  │ index.json    │    │ status.json   │    │ report.json   │               │
│  └───────────────┘    └───────────────┘    └───────┬───────┘               │
│                                                    │                        │
│                                                    ▼                        │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐               │
│  │   PHASE 5     │    │   PHASE 4     │    │   PHASE 3     │               │
│  │ Certification │◀───│  Retest Loop  │◀───│  Auto-Repair  │               │
│  │               │    │               │    │               │               │
│  │ certification │    │   (cycles)    │    │ fix_plan.json │               │
│  │ .json         │    │               │    │               │               │
│  └───────────────┘    └───────────────┘    └───────────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.8+
- PowerShell 7+ (for full Windows support) or pwsh (cross-platform)

### Installation

```bash
# Clone or copy the autonomous-workflow directory to your project
cp -r autonomous-workflow /path/to/your/repo/

# Or add as a submodule
git submodule add <url> autonomous-workflow
```

### Basic Usage

```bash
# Full autonomous run
python run_autonomous_workflow.py --repo-root /path/to/repo

# Preview without executing fixes (dry run)
python run_autonomous_workflow.py --repo-root /path/to/repo --dry-run

# Generate index only
python run_autonomous_workflow.py --repo-root /path/to/repo --mode index-only

# Verbose output
python run_autonomous_workflow.py --repo-root /path/to/repo -v
```

## Components

### Schemas (`/schemas/`)

JSON Schema definitions for all artifacts:

| Schema | Purpose |
|--------|---------|
| `automation_index.schema.json` | Canonical inventory of automation units |
| `automation_runtime_status.schema.json` | Health check execution results |
| `automation_failure_report.schema.json` | Classified failures with root causes |
| `automation_fix_plan.schema.json` | Deterministic repair strategies |
| `automation_certification.schema.json` | Certification proof artifacts |

### Collectors (`/collectors/`)

| File | Purpose |
|------|---------|
| `Invoke-AutomationHealthSweep.ps1` | PowerShell health collector |

### Orchestrator (`/orchestrator/`)

| File | Purpose |
|------|---------|
| `automation_self_healing_loop.py` | Core self-healing engine |
| `generate_index.py` | Index generator from repo scan |

### Configuration (`/config/`)

| File | Purpose |
|------|---------|
| `workflow_config.yaml` | Complete workflow configuration |

## Output Artifacts

After a run, the output directory (default: `.automation-health/`) contains:

```
.automation-health/
├── automation_index.json           # Canonical inventory
├── automation_runtime_status.json  # Health check results
├── automation_failure_report.json  # Classified failures
├── automation_fix_plan.json        # Generated fix plans
├── automation_certification.json   # Final certification
└── orchestrator_*.jsonl            # Detailed audit log
```

## Failure Classification

Failures are classified into deterministic root-cause buckets:

| Root Cause | Layer | Auto-Repairable | Fix Strategy |
|------------|-------|-----------------|--------------|
| `ENV_MISSING` | L2 - Dependencies | ✅ | Inject env defaults |
| `SCHEMA_INVALID` | L3 - Configuration | ✅ | Regenerate schema |
| `DEPENDENCY_FAIL` | L4 - Operational | ✅ | Rerun upstream |
| `TIMEOUT` | L4 - Operational | ✅ | Increase timeout |
| `NETWORK_FAIL` | L2 - Dependencies | ✅ | Retry with backoff |
| `FILE_NOT_FOUND` | L1 - Infrastructure | ✅ | Sync files |
| `PERMISSION_DENIED` | L4 - Operational | ❌ | Escalate |
| `SYNTAX_ERROR` | L5 - Business Logic | ❌ | Escalate to AI |
| `LOGIC_ERROR` | L5 - Business Logic | ❌ | Escalate to AI |

## 5-Layer Test Framework Integration

The classification aligns with the 5-Layer Test Coverage Framework:

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 5 - Business Logic    │ SYNTAX_ERROR, LOGIC_ERROR        │
├─────────────────────────────────────────────────────────────────┤
│ Layer 4 - Operational       │ TIMEOUT, PERMISSION_DENIED,      │
│                             │ DEPENDENCY_FAIL                   │
├─────────────────────────────────────────────────────────────────┤
│ Layer 3 - Configuration     │ SCHEMA_INVALID, CONFIG_INVALID   │
├─────────────────────────────────────────────────────────────────┤
│ Layer 2 - Dependencies      │ ENV_MISSING, VERSION_MISMATCH,   │
│                             │ NETWORK_FAIL                      │
├─────────────────────────────────────────────────────────────────┤
│ Layer 1 - Infrastructure    │ FILE_NOT_FOUND, RESOURCE_EXHAUSTED│
└─────────────────────────────────────────────────────────────────┘
```

## Certification

The certification artifact provides:

- **Proof of health** at a specific point in time
- **Audit trail** of all actions taken
- **Content hash** for integrity verification
- **Threshold compliance** status

### Certification Statuses

| Status | Meaning |
|--------|---------|
| `certified` | 100% success rate, all thresholds met |
| `partial` | ≥95% success rate, non-critical failures only |
| `failed` | Below threshold or critical failures |
| `expired` | Past validity period |
| `revoked` | Manually invalidated |

## Integration Points

### GitHub Actions

```yaml
# .github/workflows/automation-health.yml
name: Automation Health Check
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Autonomous Workflow
        run: |
          python autonomous-workflow/run_autonomous_workflow.py \
            --repo-root . \
            --output-dir .automation-health

      - name: Upload Certification
        uses: actions/upload-artifact@v4
        with:
          name: automation-certification
          path: .automation-health/automation_certification.json
```

### Release Gate

```yaml
# Block release if not certified
- name: Check Certification
  run: |
    STATUS=$(jq -r '.status' .automation-health/automation_certification.json)
    if [ "$STATUS" != "certified" ]; then
      echo "❌ Automation not certified: $STATUS"
      exit 1
    fi
```

### Mission Control Integration

The output JSON files can be consumed by your TUI/GUI:

```python
# Example: Load certification for dashboard
import json

with open('.automation-health/automation_certification.json') as f:
    cert = json.load(f)

print(f"Status: {cert['status']}")
print(f"Success Rate: {cert['summary']['success_rate']}%")
print(f"Failing Units: {len(cert['failing_units'])}")
```

## Configuration Reference

See `config/workflow_config.yaml` for complete configuration options.

Key settings:

```yaml
retry:
  max_cycles: 5           # Maximum self-healing attempts
  max_per_unit: 3         # Max retries per automation unit
  initial_delay: 5        # Seconds between retries
  backoff_multiplier: 2.0 # Exponential backoff

certification:
  minimum_success_rate: 100.0  # Required for certification
  max_failures:
    critical: 0           # Zero tolerance for critical
    high: 0               # Zero tolerance for high
```

## CLI Reference

```
usage: run_autonomous_workflow.py [-h] --repo-root REPO_ROOT
                                  [--output-dir OUTPUT_DIR]
                                  [--mode {full,discover,index-only,validate,certify-only}]
                                  [--status-file STATUS_FILE]
                                  [--report REPORT]
                                  [--max-retries MAX_RETRIES]
                                  [--retry-delay RETRY_DELAY]
                                  [--threshold THRESHOLD]
                                  [--dry-run] [--verbose]

Options:
  --repo-root PATH       Repository root path (required)
  --output-dir PATH      Output directory (default: .automation-health)
  --mode MODE            Execution mode (default: full)
  --status-file PATH     Use existing runtime status file
  --report PATH          Path to AUTOMATION_COMPONENTS_REPORT.md
  --max-retries N        Maximum retry cycles (default: 5)
  --retry-delay N        Initial retry delay in seconds (default: 5)
  --threshold N          Success rate threshold (default: 100.0)
  --dry-run              Preview actions without executing
  --verbose, -v          Enable verbose logging
```

## Extending the System

### Adding New Root Causes

1. Add to `RootCause` enum in `automation_self_healing_loop.py`
2. Add pattern in `ERROR_PATTERNS` dictionary
3. Map to fix strategy in `ROOT_CAUSE_TO_FIX`
4. Optionally add to `AUTO_REPAIRABLE` set

### Adding New Fix Strategies

1. Add to `FixStrategy` enum
2. Implement in `generate_fix_plan()` method
3. Document in `workflow_config.yaml`

### Custom Validators

Extend `Invoke-HealthCheck` in the PowerShell collector or create custom validation scripts.

## Troubleshooting

### PowerShell Not Available

On Linux/macOS, install PowerShell:
```bash
# Ubuntu/Debian
sudo apt-get install -y powershell

# macOS
brew install powershell/tap/powershell
```

Or use Python-only mode (limited validation).

### Permission Issues

Ensure scripts are executable:
```bash
chmod +x run_autonomous_workflow.py
chmod +x orchestrator/*.py
```

### Large Repositories

For repos with 1000+ automation units:
- Use `--mode index-only` first to review discovery
- Adjust timeouts in config
- Consider running in parallel (future enhancement)

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the workflow on itself (`--repo-root .`)
5. Submit a pull request

---

**Built for zero-touch operation with comprehensive audit trails.**
