# Scripts Directory

**Purpose**: Utility scripts for repository-wide checks and automation.

**Status**: Active

---

## Contents

| File | Description |
|------|-------------|
| `readme_presence_scan.py` | Scans directories to verify README coverage |
| `Schedule-ZeroTouchAutomation.ps1` | Scheduler for zero-touch automation |
| `Test-ZeroTouchAutomation.ps1` | Test harness for zero-touch automation |
| `README.yaml` | Machine-readable directory metadata |

---

## Usage

### README Presence Scan

Audit repository structure for README coverage:

```bash
python readme_presence_scan.py --path ../
```

### Zero-Touch Automation

```powershell
# Test zero-touch automation
.\Test-ZeroTouchAutomation.ps1

# Schedule automation
.\Schedule-ZeroTouchAutomation.ps1 -Interval 60
```

---

## Extending

Add new repository checks following the pattern:

1. Create new script (`.py` or `.ps1`)
2. Add usage documentation
3. Update this README

---

## Related

- `../automation/` - Automation utilities
- `../tests/` - Test scripts for executors
