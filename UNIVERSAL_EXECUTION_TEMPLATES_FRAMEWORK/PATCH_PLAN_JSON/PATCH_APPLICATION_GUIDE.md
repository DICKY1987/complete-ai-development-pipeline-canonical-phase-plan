# UET V2 Master Plan - Patch Application Guide

**Version**: 1.0.0  
**Last Updated**: 2025-11-23T11:07:25Z  
**Purpose**: Instructions for applying patches to master plan

---

## Available Patches

| Patch ID | File | Priority | Operations | Status |
|----------|------|----------|------------|--------|
| 001 | `001-config-integration.json` | CRITICAL | 22 | Ready |
| 002 | `002-documentation-integration.json` | CRITICAL | 15 | Ready |
| 003 | `003-uet-v2-specifications.json` | CRITICAL | 25 | Ready |
| 004 | `004-planning-reference.json` | CRITICAL | 18 | Ready |

**Total Operations**: 80 patches ready to apply

---

## Patch 003: UET V2 Specifications

**Source Files**:
- `docs/uet_v2/STATE_MACHINES.md`
- `docs/uet_v2/COMPONENT_CONTRACTS.md`
- `docs/uet_v2/DAG_SCHEDULER.md`
- `docs/uet_v2/FILE_SCOPE.md`
- `docs/uet_v2/INTEGRATION_POINTS.md`

**What It Adds**:
1. State machine definitions (Worker, Patch Ledger, Test Gate)
2. Component API contracts (10 components)
3. DAG scheduler with 4 dependency types
4. File scope access modes and isolation
5. Component integration points and call graph
6. State machine validation rules
7. File scope enforcement
8. DAG cycle detection

**Impact**:
- Defines ALL UET V2 component behavior
- Enables parallel development (contracts)
- Provides conflict detection (file scope)
- Prevents circular dependencies (integration points)
- Foundation for ALL implementation phases

---

## Patch 001: Config Integration

**Source Files**:
- `CODEBASE_INDEX.yaml`
- `ai_policies.yaml`
- `QUALITY_GATE.yaml`
- `PROJECT_PROFILE.yaml`
- `PRO_Phase Specification mandatory structure.md`

**What It Adds**:
1. Architecture metadata (4-layer model)
2. Three-engine problem documentation
3. System alignment status (40% → 100%)
4. Existing components inventory
5. AI policies and edit zones
6. Project metadata and constraints
7. Quality gates (30+ gates)
8. Phase specification requirements
9. **Phase 7**: Engine Unification (24 hours)

**Impact**:
- Adds critical metadata for AI understanding
- Documents existing 40% implementation
- Adds engine unification phase
- Defines quality gates and CI enforcement

---

## Patch 002: Documentation Integration

**Source Files**:
- `docs/tools-instructions-config.md`
- `docs/soft-sandbox-pattern.md`
- `docs/DOCUMENTATION_INDEX.md`
- `docs/ACS_USAGE_GUIDE.md`

**What It Adds**:
1. AI tool configuration (3-layer instruction pattern)
2. Sandbox strategy (soft sandbox pattern)
3. Documentation structure and ACS artifacts
4. Future AI techniques (GraphRAG, RAPTOR, etc.)
5. Documentation validation gates
6. Pre-flight checks for sandbox
7. **WS-000-007**: AI Tool Instruction Files workstream (1.5 hours)

**Impact**:
- Defines multi-tool instruction pattern
- Adds sandbox safety requirements
- Increases Phase 0 from 4.5h → 6.0h
- Adds documentation validation

---

## How to Apply Patches

### Method 1: Python jsonpatch Library (Recommended)

```python
import json
import jsonpatch
from pathlib import Path

# Load base plan
base_plan_path = Path("../copiolt plan_uv2.json")
base_plan = json.loads(base_plan_path.read_text())

# Load patches
patch_001 = json.loads(Path("001-config-integration.json").read_text())
patch_002 = json.loads(Path("002-documentation-integration.json").read_text())

# Apply patches
plan = jsonpatch.apply_patch(base_plan, patch_001)
plan = jsonpatch.apply_patch(plan, patch_002)

# Save merged plan
output_path = Path("UET_V2_MASTER_PLAN.json")
output_path.write_text(json.dumps(plan, indent=2))

print(f"✅ Applied {len(patch_001) + len(patch_002)} operations")
print(f"✅ Master plan saved to: {output_path}")
```

### Method 2: Manual Python Script

```python
import json
from pathlib import Path

def apply_patch_operation(obj, op):
    """Apply a single RFC 6902 operation."""
    path = op['path'].strip('/').split('/')
    
    if op['op'] == 'add':
        target = obj
        for key in path[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[path[-1]] = op['value']
    
    elif op['op'] == 'replace':
        target = obj
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = op['value']
    
    elif op['op'] == 'remove':
        target = obj
        for key in path[:-1]:
            target = target[key]
        del target[path[-1]]
    
    return obj

# Load base plan
base_plan = json.loads(Path("../copiolt plan_uv2.json").read_text())

# Load and apply patch 001
patch_001 = json.loads(Path("001-config-integration.json").read_text())
for operation in patch_001:
    base_plan = apply_patch_operation(base_plan, operation)

# Load and apply patch 002
patch_002 = json.loads(Path("002-documentation-integration.json").read_text())
for operation in patch_002:
    base_plan = apply_patch_operation(base_plan, operation)

# Save result
Path("UET_V2_MASTER_PLAN.json").write_text(json.dumps(base_plan, indent=2))
print("✅ Master plan created")
```

### Method 3: PowerShell

```powershell
# Load base plan
$basePlan = Get-Content "../copiolt plan_uv2.json" -Raw | ConvertFrom-Json

# Load patches
$patch001 = Get-Content "001-config-integration.json" -Raw | ConvertFrom-Json
$patch002 = Get-Content "002-documentation-integration.json" -Raw | ConvertFrom-Json

# Apply patches (simplified - real implementation needs RFC 6902 logic)
foreach ($op in $patch001) {
    if ($op.op -eq "add") {
        # Add logic here
        Write-Host "Applying: $($op.path)"
    }
}

# Save merged plan
$basePlan | ConvertTo-Json -Depth 100 | Out-File "UET_V2_MASTER_PLAN.json"
Write-Host "✅ Master plan created"
```

---

## Validation After Applying Patches

### 1. Validate JSON Structure

```powershell
# Ensure valid JSON
Get-Content UET_V2_MASTER_PLAN.json -Raw | ConvertFrom-Json | Out-Null
if ($?) { Write-Host "✅ Valid JSON" } else { Write-Host "❌ Invalid JSON" }
```

### 2. Check ULID Uniqueness

```python
import json
from pathlib import Path
from collections import Counter

plan = json.loads(Path("UET_V2_MASTER_PLAN.json").read_text())

# Extract all ULIDs
ulids = []

def extract_ulids(obj, path=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.endswith('_ulid'):
                ulids.append(value)
            extract_ulids(value, f"{path}/{key}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            extract_ulids(item, f"{path}[{i}]")

extract_ulids(plan)

# Check for duplicates
duplicates = [ulid for ulid, count in Counter(ulids).items() if count > 1]

if duplicates:
    print(f"❌ Duplicate ULIDs found: {duplicates}")
else:
    print(f"✅ All {len(ulids)} ULIDs are unique")
```

### 3. Validate Dependency Graph

```python
def check_dependencies(plan):
    """Ensure no circular dependencies."""
    phases = plan.get('phases', {})
    
    def has_cycle(phase_id, visited, stack):
        visited.add(phase_id)
        stack.add(phase_id)
        
        phase = phases.get(phase_id, {})
        for dep in phase.get('dependencies', []):
            if dep not in visited:
                if has_cycle(dep, visited, stack):
                    return True
            elif dep in stack:
                return True
        
        stack.remove(phase_id)
        return False
    
    for phase_id in phases:
        if has_cycle(phase_id, set(), set()):
            print(f"❌ Circular dependency detected in {phase_id}")
            return False
    
    print("✅ No circular dependencies")
    return True

plan = json.loads(Path("UET_V2_MASTER_PLAN.json").read_text())
check_dependencies(plan)
```

### 4. Validate Against Schema (If Available)

```python
import jsonschema

# If you have a schema file
schema = json.loads(Path("schema/master_plan.schema.json").read_text())
plan = json.loads(Path("UET_V2_MASTER_PLAN.json").read_text())

try:
    jsonschema.validate(plan, schema)
    print("✅ Schema validation passed")
except jsonschema.ValidationError as e:
    print(f"❌ Schema validation failed: {e}")
```

---

## What the Merged Plan Will Contain

### Metadata Sections
- `meta/patch_metadata` - Patch application history
- `meta/architecture` - 4-layer architecture
- `meta/three_engine_problem` - Engine unification requirements
- `meta/system_alignment` - 40% → 100% migration strategy
- `meta/existing_components` - What's already built
- `meta/ai_policies` - Edit zones and invariants
- `meta/project` - Project identification
- `meta/constraints` - Patch-only mode, line limits
- `meta/framework_paths` - Directory structure
- `meta/phase_specification` - Mandatory phase structure
- `meta/ai_tool_configuration` - Multi-tool instruction pattern
- `meta/sandbox_strategy` - Safety isolation
- `meta/documentation_structure` - ACS artifacts
- `meta/future_ai_techniques` - Advanced patterns

### Validation Sections
- `validation/quality_gates` - 30+ gates
- `validation/execution_order` - Pre-commit, full validation
- `validation/ai_policy_compliance` - Import path enforcement
- `validation/ci_enforcement` - CI/CD integration
- `validation/documentation_gates` - ACS conformance

### Phases
- **PH-000**: Foundation Infrastructure (6.0 hours, 7 workstreams)
- **PH-001**: Schema Foundation (2.0 hours, 3 workstreams)
- **PH-007**: Engine Unification (24 hours, 3 workstreams) - NEW

### Updated Timeline
- **Original**: 280 hours (7 weeks)
- **With 40% existing**: 168 hours
- **With unification**: 192 hours
- **With overhead**: 200 hours (8 weeks realistic)

---

## Installation of jsonpatch (if needed)

```bash
pip install jsonpatch
```

---

## Next Steps After Applying Patches

1. **Validate** the merged plan (use validation scripts above)
2. **Review** the new Phase 7 (Engine Unification)
3. **Update** timeline estimates
4. **Create** `.github/copilot-instructions.md` if missing
5. **Create** `CLAUDE.md` if missing
6. **Update** `AGENTS.md` with Codex-specific instructions
7. **Set up** sandbox directories (`C:\Users\richg\AI_SANDBOX`, `~/ai-sandbox`)

---

## Troubleshooting

### Issue: "Key already exists"
**Solution**: Patch 001 and 002 should not overlap. If error occurs, check which patch added the key first.

### Issue: "Invalid path"
**Solution**: Ensure base plan has required parent keys. May need to add empty objects first.

### Issue: "Duplicate ULIDs"
**Solution**: Regenerate ULIDs for conflicting entries. Each ULID must be globally unique.

---

**Ready to apply patches?**

Run: `python apply_patches.py` (script in next section)
