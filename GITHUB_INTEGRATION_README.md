# GitHub Integration v2 - Quick Start

## 🎉 Complete Implementation

All GitHub Projects v2 integration features are **production-ready**.

## What You Get

✅ **Pattern-based architecture** (PAT-GH-SYNC-PHASE-001)
✅ **Full GraphQL Projects v2 support** (all field types)
✅ **CLI sync tool** with dry-run mode
✅ **Automatic validation** (PAT-CHECK-001 compliant)
✅ **GitHub Actions** for auto-sync
✅ **8 unit tests** (all passing)
✅ **Comprehensive docs** with examples

## Installation (2 minutes)

```bash
# 1. Install dependencies
pip install pyyaml requests jsonschema

# 2. Set your GitHub token
export GITHUB_TOKEN="ghp_your_personal_access_token"

# 3. Verify installation
python scripts/validate_phase_plan.py \
  --repo-root . \
  --phase-file MASTER_SPLINTER_Phase_Plan_Template.yml
```

Expected output:
```
✓ STEP_1_PATTERN_REGISTRY_AND_GH_SYNC: PASS
✓ STEP_2_SPLINTER_PHASE_SCHEMA: PASS
✓ STEP_3_GH_SYNC_SCHEMA: PASS

Overall: True ✓
```

## Usage

### 1. Configure Your Phase Plan

Add `github_integration` block (or use updated template):

```yaml
github_integration:
  enabled: true
  repo:
    owner: "YOUR_USERNAME"
    name: "YOUR_REPO"
  project:
    owner: "YOUR_USERNAME"
    project_number: 1
```

### 2. Dry Run (Preview)

```bash
python scripts/splinter_sync_phase_to_github.py \
  --phase-file phases/my_phase.yaml \
  --github-repo YOUR_USERNAME/YOUR_REPO \
  --dry-run
```

### 3. Sync to GitHub

```bash
python scripts/splinter_sync_phase_to_github.py \
  --phase-file phases/my_phase.yaml \
  --github-repo YOUR_USERNAME/YOUR_REPO
```

### 4. Automatic Sync (Optional)

Push to your repo and let GitHub Actions handle it:

```bash
git add phases/my_phase.yaml
git commit -m "Add phase plan"
git push
```

## Documentation

📖 **Start here**: `GITHUB_INTEGRATION_V2_COMPLETE.md` - Complete overview
📖 **Installation**: `GITHUB_INTEGRATION_INSTALL.md` - Setup guide
📖 **Quick Ref**: `GITHUB_INTEGRATION_QUICK_REF.md` - Commands
📖 **Example**: `patterns/executors/github_sync/EXAMPLE.md` - Walkthrough
📖 **Full Guide**: `MASTER_SPLINTER_GITHUB_ADD_ON.md` - Original spec

## File Structure

```
patterns/
├── executors/github_sync/
│   ├── phase_sync.py          ← Core implementation (554 lines)
│   ├── README.md              ← Feature docs
│   └── EXAMPLE.md             ← End-to-end example
├── registry/PATTERN_INDEX.yaml ← Pattern registry
├── specs/GH_SYNC_PHASE_V1.pattern.yaml
├── schemas/
│   ├── GH_SYNC_PHASE_V1.schema.json
│   └── SPLINTER_PHASE_PLAN_V1.schema.json
└── tests/GH_SYNC_PHASE_V1_test.py  ← 8 unit tests

scripts/
├── validate_phase_plan.py     ← Validator
└── splinter_sync_phase_to_github.py  ← CLI sync (202 lines)

.github/workflows/
└── splinter_phase_sync.yml    ← Auto-sync workflow
```

## Features

### ✅ GitHub Issues
- Create/update issues automatically
- Template-based titles and bodies
- Auto-generated labels (workstream, phase)
- Assignee support

### ✅ GitHub Projects v2
- Automatic project resolution (user/org)
- Find/create project items
- Update custom fields:
  - TEXT (Phase ID, Workstream, doc_id)
  - SINGLE_SELECT (Status, Risk)
  - DATE (Target date)
  - NUMBER (Story points)
- Field type auto-detection
- Pagination for large projects

### ✅ Validation
- Schema validation (JSON Schema)
- Pattern compliance (PAT-CHECK-001)
- 3-step validation process
- Machine-readable reports

### ✅ Testing
- 8 unit tests (all passing)
- Mock-based (no API calls required)
- Fast execution (<0.01s)

## Requirements

- **Python**: 3.11+
- **GitHub Token**: Personal access token with `repo` and `project` scopes
- **GitHub Project v2**: Created with custom fields

## Support

All error messages are descriptive and actionable. Common issues:

- **"GraphQL error: Could not resolve to a ProjectV2"**
  → Check `project_number` and token permissions

- **"Field 'Status' not found in project"**
  → Verify custom field names match exactly

- **"Option 'planned' not found for single-select field"**
  → Ensure single-select options exist in project

See `patterns/executors/github_sync/EXAMPLE.md` for troubleshooting.

## Version

**v2.0** (2025-12-04) - Complete implementation
All core features implemented, tested, and documented.

## License

Part of the SPLINTER Phase Plan system.

---

**Status: Production Ready 🚀**

Run tests: `python patterns/tests/GH_SYNC_PHASE_V1_test.py -v`
Validate: `python scripts/validate_phase_plan.py --repo-root . --phase-file ...`
Sync: `python scripts/splinter_sync_phase_to_github.py --phase-file ... --github-repo ...`
