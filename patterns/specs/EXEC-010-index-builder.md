# EXEC-010: Category Index Builder Pattern
# Pattern for creating comprehensive category index files

**Pattern ID**: EXEC-010
**Name**: Category Index Builder
**Category**: Documentation
**Time Savings**: 85-90% vs manual
**Difficulty**: Low
**Prerequisites**: Completed EXEC-009 (doc_ids registered)

---

## Purpose

Create structured YAML index files that map doc_ids to files, dependencies, and metadata.

---

## Pattern Structure

### Discovery Phase (5 minutes)

**Input**: Category with registered doc_ids

**Actions**:
1. List all doc_ids in category
2. Map doc_ids to file paths
3. Identify module relationships
4. Extract metadata from files

**Output**: Category structure

**Example**:
```powershell
# Discover registered doc_ids for category
python scripts/doc_id_registry_cli.py list --category core

# Output mapping:
# DOC-CORE-STATE-DB-001 → core/state/db.py
# DOC-CORE-STATE-CRUD-002 → core/state/crud.py
# DOC-CORE-ORCHESTRATOR-005 → core/engine/orchestrator.py
```

### Template Phase (10 minutes)

**Input**: Existing index file (e.g., CORE_MODULE_INDEX.yaml)

**Actions**:
1. Copy structure from existing index
2. Identify invariant sections (metadata, structure)
3. Mark variable sections (entries, counts)
4. Create template with placeholders

**Output**: Index template

**Example Template**:
```yaml
# {CATEGORY}_INDEX.yaml
# Index of {category_description}
# Generated: {date}

metadata:
  category: {category}
  description: "{description}"
  total_modules: {count}
  last_updated: "{date}"

{section_1}:
  - doc_id: {DOC_ID}
    name: {module_name}
    module: {python_module}
    file: {file_path}
    test_file: {test_path}
    purpose: "{purpose}"
    responsibilities:
      - {responsibility_1}
      - {responsibility_2}
    priority: {priority}
    status: active
```

### Fill Phase (15 minutes per category)

**Input**: Template + doc_id list + files

**Actions**:
1. For each doc_id, extract metadata
2. Fill template fields
3. Group by subcategory
4. Add dependencies if applicable
5. Add import patterns

**Output**: Completed index file

**Example**:
```powershell
# Auto-generate index entries
$docIds = @(
    @{id="DOC-SPEC-WORKSTREAM-SCHEMA-001"; file="schema/workstream.schema.json"},
    @{id="DOC-SPEC-STEP-SCHEMA-002"; file="schema/step.schema.json"},
    @{id="DOC-SPEC-ERROR-SCHEMA-003"; file="schema/error.schema.json"}
)

# Build index structure
$index = @{
    metadata = @{
        category = "spec"
        description = "JSON schemas and specifications"
        total_modules = $docIds.Count
        last_updated = Get-Date -Format "yyyy-MM-dd"
    }
    schemas = @()
}

foreach ($doc in $docIds) {
    $basename = Split-Path $doc.file -Leaf
    $name = $basename -replace "\.schema\.json$", ""

    $entry = @{
        doc_id = $doc.id
        name = $name
        file = $doc.file
        schema_type = "json-schema-draft-07"
        purpose = "$name schema definition"
        validates = "$name objects"
        priority = "high"
        status = "active"
    }

    $index.schemas += $entry
}

# Output to YAML
$index | ConvertTo-Yaml | Out-File specifications/SPEC_INDEX.yaml
```

### Enrich Phase (10 minutes)

**Input**: Basic index

**Actions**:
1. Add dependency relationships
2. Add import patterns
3. Add AI assistance metadata
4. Add edit policies

**Output**: Enriched index

**Example**:
```yaml
# Add dependencies section
dependencies:
  DOC-CORE-ORCHESTRATOR-005:
    depends_on:
      - DOC-CORE-SCHEDULER-006
      - DOC-CORE-EXECUTOR-007
      - DOC-CORE-STATE-DB-001
    used_by:
      - DOC-CORE-RECOVERY-010

# Add import patterns
import_patterns:
  - pattern: "from core.state.db import init_db"
    doc_id: DOC-CORE-STATE-DB-001
  - pattern: "from core.engine.orchestrator import Orchestrator"
    doc_id: DOC-CORE-ORCHESTRATOR-005

# Add AI metadata
ai_priority:
  high:
    - DOC-CORE-ORCHESTRATOR-005
    - DOC-CORE-STATE-DB-001
  medium:
    - DOC-CORE-SCHEDULER-006

# Add edit policy
edit_policy:
  safe:
    - All modules are safe to edit
    - Follow import path standards
    - Add DOC_LINK to new files
```

### Verification Phase (2 minutes)

**Input**: Completed index

**Actions**:
1. Validate YAML syntax
2. Check all doc_ids exist in registry
3. Verify file paths are correct
4. Count matches expected

**Output**: Validated index

**Example**:
```powershell
# Validate YAML syntax
$yaml = Get-Content specifications/SPEC_INDEX.yaml -Raw
$parsed = ConvertFrom-Yaml $yaml

# Check counts
$expectedCount = ($parsed.schemas).Count
Write-Host "Index contains $expectedCount entries"

# Verify doc_ids exist
foreach ($schema in $parsed.schemas) {
    $exists = python scripts/doc_id_registry_cli.py search --pattern $schema.doc_id
    if (!$exists) {
        Write-Host "⚠️ Doc ID not found: $($schema.doc_id)" -ForegroundColor Yellow
    }
}
```

---

## Decision Elimination

### Pre-Decisions (Make Once)
- ✅ **Index structure**: Copy from existing (CORE_MODULE_INDEX.yaml)
- ✅ **Sections**: Group by logical subcategory
- ✅ **Required fields**: doc_id, name, file, purpose, status
- ✅ **Optional fields**: dependencies, import patterns
- ✅ **File location**: {category}/{CATEGORY}_INDEX.yaml

### Not Decisions (Don't Waste Time)
- ❌ **Perfect descriptions**: One sentence is enough
- ❌ **Complete dependencies**: Add obvious ones only
- ❌ **All import patterns**: 3-5 examples sufficient
- ❌ **Exhaustive metadata**: Core fields only

---

## Time Breakdown

**For 25-file category:**

| Phase | Manual | Pattern | Savings |
|-------|--------|---------|---------|
| Discovery | 30 min | 5 min | 83% |
| Template | 45 min | 10 min | 78% |
| Fill | 125 min (5 min × 25) | 15 min | 88% |
| Enrich | 60 min | 10 min | 83% |
| Verification | 15 min | 2 min | 87% |
| **Total** | **275 min** | **42 min** | **85%** |

---

## Example: Complete Workflow

```powershell
# 1. DISCOVERY
cd .worktrees/wt-docid-specs

# List registered spec doc_ids
python ../../scripts/doc_id_registry_cli.py list --category spec > spec_docids.txt

# Map to files
$specs = @(
    @{id="DOC-SPEC-WORKSTREAM-SCHEMA-001"; file="schema/workstream.schema.json"},
    @{id="DOC-SPEC-STEP-SCHEMA-002"; file="schema/step.schema.json"},
    @{id="DOC-SPEC-ERROR-SCHEMA-003"; file="schema/error.schema.json"}
)

# 2. TEMPLATE (copy from CORE_MODULE_INDEX.yaml)
Copy-Item ../../core/CORE_MODULE_INDEX.yaml ../../specifications/SPEC_INDEX.yaml

# Edit to match spec category
# Replace: category: core → category: spec
# Replace: core modules → JSON schemas
# Remove: core-specific sections

# 3. FILL
# Create index entries for each schema
$indexEntries = foreach ($spec in $specs) {
    @"
  - doc_id: $($spec.id)
    name: $(Split-Path $spec.file -Leaf -Replace '\.schema\.json$','')
    file: $($spec.file)
    schema_type: json-schema-draft-07
    purpose: "Schema for $(Split-Path $spec.file -Leaf -Replace '\.schema\.json$','')"
    priority: high
    status: active
"@
}

# Append to index file (replace schemas: section)
# (Manual editing or script automation)

# 4. ENRICH
# Add validation metadata
@"
validation:
  tool: ajv
  command: "ajv validate -s {schema} -d {data}"

schema_registry:
  - DOC-SPEC-WORKSTREAM-SCHEMA-001
  - DOC-SPEC-STEP-SCHEMA-002
  - DOC-SPEC-ERROR-SCHEMA-003
"@ | Out-File ../../specifications/SPEC_INDEX.yaml -Append

# 5. VERIFY
python ../../scripts/doc_id_registry_cli.py validate

# Check YAML syntax
$yaml = Get-Content ../../specifications/SPEC_INDEX.yaml -Raw
ConvertFrom-Yaml $yaml

Write-Host "✅ Index created and validated" -ForegroundColor Green

# 6. COMMIT
git add ../../specifications/SPEC_INDEX.yaml
git commit -m "feat: create specification index (8 schemas)"
```

---

## Index File Templates

### Template 1: Module Index (Core, Error, AIM)
```yaml
# {CATEGORY}_INDEX.yaml

metadata:
  category: {category}
  description: "{description}"
  total_modules: {count}
  last_updated: "{date}"

# Group by logical sections
{section_name}:
  - doc_id: {DOC_ID}
    name: {name}
    module: {python.module.path}
    file: {relative/path/to/file.py}
    test_file: tests/{category}/test_{name}.py
    purpose: "{one_sentence_description}"
    responsibilities:
      - {what_it_does_1}
      - {what_it_does_2}
    priority: {high|medium|low}
    status: active
    dependencies:  # optional
      - {DOC_ID_DEPENDS_ON}

dependencies:
  {DOC_ID}:
    depends_on:
      - {dependency_doc_id}
    used_by:
      - {consumer_doc_id}

import_patterns:
  - pattern: "from {module} import {class}"
    doc_id: {DOC_ID}

ai_priority:
  high: [list of critical doc_ids]
  medium: [list of important doc_ids]

edit_policy:
  safe: [guidelines for editing]
```

### Template 2: Schema Index
```yaml
# SPEC_INDEX.yaml

metadata:
  category: spec
  description: "JSON schemas and specifications"
  total_schemas: {count}
  last_updated: "{date}"

schemas:
  - doc_id: {DOC_ID}
    name: {schema_name}
    file: schema/{name}.schema.json
    schema_type: json-schema-draft-07
    purpose: "{what_it_validates}"
    validates: "{data_type} objects"
    priority: high
    status: active

validation:
  tool: ajv
  command: "ajv validate -s {schema} -d {data}"

schema_registry: [list of all schema doc_ids]
```

### Template 3: Script Index
```yaml
# SCRIPT_INDEX.yaml

metadata:
  category: script
  description: "Automation scripts and tools"
  total_scripts: {count}
  last_updated: "{date}"

scripts:
  - doc_id: {DOC_ID}
    name: {script_name}
    file: scripts/{name}.py
    purpose: "{what_it_does}"
    usage: "python scripts/{name}.py [options]"
    required_args: [{arg1}, {arg2}]
    optional_args: [{arg3}]
    output: "{what_it_produces}"
    priority: {high|medium|low}
    status: active

execution_order:
  phase_1: [scripts for phase 1]
  phase_2: [scripts for phase 2]
```

### Template 4: Test Index
```yaml
# TEST_INDEX.yaml

metadata:
  category: test
  description: "Test suites"
  total_tests: {count}
  last_updated: "{date}"

tests:
  - doc_id: {DOC_ID}
    name: test_{module}
    file: tests/{category}/test_{module}.py
    tests_module: {DOC_ID_OF_MODULE_UNDER_TEST}
    test_type: {unit|integration|e2e}
    coverage_target: {percentage}
    priority: {high|medium|low}
    status: active

test_execution:
  command: "pytest tests/{category}/test_{module}.py"
  markers: [list of pytest markers]
```

---

## Anti-Patterns to Avoid

❌ **Build index before registering doc_ids** → Register first
❌ **Create new structure for each category** → Reuse template
❌ **Manual YAML construction** → Use scripts/helpers
❌ **Include every possible field** → Core fields only
❌ **Skip verification** → Always validate

---

## Success Criteria

- ✅ Index file created in correct location
- ✅ All registered doc_ids included
- ✅ YAML validates (no syntax errors)
- ✅ File paths are correct
- ✅ Metadata counts match actual
- ✅ Time: <2 min per entry

---

## Integration with EXEC-009

```powershell
# Complete workflow: Register → Index → Commit

# Step 1: Register (EXEC-009)
# ... register all modules in category ...

# Step 2: Build Index (EXEC-010)
# ... create category index file ...

# Step 3: Commit together
git add DOC_ID_REGISTRY.yaml
git add {category}/{CATEGORY}_INDEX.yaml
git commit -m "feat: register and index {category} modules ({count} files)"
```

---

## Proven Results

**From Phase 1 & 2:**
- Created CORE_MODULE_INDEX.yaml (10 modules) in 15 minutes
- Created ERROR_PLUGIN_INDEX.yaml (10 modules) in 15 minutes
- **Manual estimate**: 2 hours each
- **Savings**: 87.5% per index

---

**DOC_LINK**: DOC-PAT-EXECUTION-DOCID-INDEX-BUILDER-001
