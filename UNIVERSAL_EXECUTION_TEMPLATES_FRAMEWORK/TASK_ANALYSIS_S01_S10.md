# Task Analysis & Pattern Development for S01-S10

**Analysis Date**: 2025-11-24  
**Purpose**: Break down each step into atomic tasks and develop execution patterns  
**Scope**: Steps S01 through S10 of Pattern Governance Phase  

---

## STEP S01: Create OPERATION_KIND_REGISTRY.yaml

### Task Breakdown

#### T01.1: Research & Design
**Duration**: 5 minutes  
**Tasks**:
- Review `assistant_responses_operation_kinds.md` for OPK naming conventions
- Review existing patterns in PATTERN_INDEX.yaml to identify common operations
- Review PAT-CHECK-001 for OPK format requirements
- Design OPK categorization scheme (filesystem, code_edit, testing, docs, git, etc.)

**Inputs**:
- `patterns/assistant_responses_operation_kinds.md`
- `patterns/registry/PATTERN_INDEX.yaml`
- `patterns/PAT-CHECK-001  Pattern Directory & ID System Compliance (v2).md`

**Outputs**:
- Mental model of OPK categories
- List of 20-25 candidate operation kinds

---

#### T01.2: Define Core Operation Kinds
**Duration**: 5 minutes  
**Tasks**:
- Define filesystem operations: CREATE_FILE, SAVE_FILE, DELETE_FILE, MOVE_FILE, etc.
- Define code editing operations: APPLY_PATCH, REFACTOR_MODULE, ADD_FUNCTION, etc.
- Define testing operations: RUN_TESTS, RUN_LINTER, RUN_FORMATTER, etc.
- Define documentation operations: CREATE_DOC, UPDATE_DOC, UPDATE_INDEX, etc.
- Define git operations: CREATE_WORKTREE, MERGE_WORKTREE, OPEN_PULL_REQUEST, etc.
- Define orchestration operations: PROCESS_PATCHES, SEARCH_FILES, VALIDATE_COMPLIANCE, etc.

**Outputs**:
- 20-25 operation kinds with names, categories, summaries

---

#### T01.3: Create YAML Structure
**Duration**: 3 minutes  
**Tasks**:
- Create YAML header (version, status, metadata)
- Format each OPK with required fields: id, name, category, summary, examples, required_params, optional_params, notes
- Assign sequential OPK IDs: OPK-0001, OPK-0002, etc.
- Validate YAML syntax

**Template**:
```yaml
version: 1.0.0
status: stable
metadata:
  created: "2025-11-24"
  total_operation_kinds: 25

operation_kinds:
  - id: OPK-0001
    name: CREATE_FILE
    category: filesystem
    summary: Create a new file with optional template content
    examples:
      - "create new file"
      - "add file to project"
    required_params:
      - path
    optional_params:
      - template_ref
      - doc_id
    notes:
      - "Use SAVE_FILE for writing content to existing files"
```

**Outputs**:
- `patterns/registry/OPERATION_KIND_REGISTRY.yaml`

---

#### T01.4: Validate & Test
**Duration**: 2 minutes  
**Tasks**:
- Validate YAML syntax (PowerShell or Python)
- Check all required fields present
- Verify ID sequence is correct
- Verify name format (SCREAMING_SNAKE_CASE)

**Validation Commands**:
```powershell
# PowerShell validation
Get-Content patterns/registry/OPERATION_KIND_REGISTRY.yaml | ConvertFrom-Yaml
```

```python
# Python validation
import yaml
with open('patterns/registry/OPERATION_KIND_REGISTRY.yaml') as f:
    data = yaml.safe_load(f)
    assert 'operation_kinds' in data
    assert len(data['operation_kinds']) >= 20
```

---

### Pattern for S01: CREATE_REGISTRY_FILE

```yaml
pattern_id: PAT-CREATE-REGISTRY-001
operation_kind: CREATE_REGISTRY_FILE
steps:
  1_research:
    - read_reference_docs
    - identify_required_structure
    - list_candidate_entries
  2_define:
    - categorize_entries
    - assign_ids
    - write_summaries
  3_create:
    - write_yaml_header
    - format_entries
    - validate_syntax
  4_validate:
    - check_required_fields
    - verify_format
    - test_parseability
```

**Estimated**: 15 minutes ✅

---

## STEP S02: Update PATTERN_INDEX.yaml

### Task Breakdown

#### T02.1: Backup Existing Index
**Duration**: 1 minute  
**Tasks**:
- Copy current PATTERN_INDEX.yaml to backup
- Name backup with timestamp: `PATTERN_INDEX.yaml.backup_YYYYMMDD_HHMMSS`

**Commands**:
```powershell
Copy-Item patterns/registry/PATTERN_INDEX.yaml `
  patterns/registry/PATTERN_INDEX.yaml.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')
```

---

#### T02.2: Analyze Current Structure
**Duration**: 2 minutes  
**Tasks**:
- Count total patterns (currently 24)
- Identify patterns with `doc_id` vs. without
- Identify patterns with `operation_kinds` vs. without
- List any structural issues

**Analysis Script**:
```python
import yaml

with open('patterns/registry/PATTERN_INDEX.yaml') as f:
    index = yaml.safe_load(f)

patterns = index['patterns']
with_doc_id = [p for p in patterns if 'doc_id' in p]
without_doc_id = [p for p in patterns if 'doc_id' not in p]
with_opk = [p for p in patterns if 'operation_kinds' in p]

print(f"Total patterns: {len(patterns)}")
print(f"With doc_id: {len(with_doc_id)}")
print(f"Without doc_id: {len(without_doc_id)}")
print(f"With operation_kinds: {len(with_opk)}")
```

---

#### T02.3: Generate doc_id for Missing Patterns
**Duration**: 3 minutes  
**Tasks**:
- For each pattern without `doc_id`:
  - Generate format: `DOC-PAT-<PATTERN-NAME>-001`
  - Validate format matches `[A-Z0-9]+(-[A-Z0-9]+)*`
  - Check for duplicates

**Generation Logic**:
```python
def generate_doc_id(pattern_id: str) -> str:
    # PAT-ATOMIC-CREATE-001 -> DOC-PAT-ATOMIC-CREATE-001
    if pattern_id.startswith('PAT-'):
        return f"DOC-{pattern_id}"
    else:
        return f"DOC-PAT-{pattern_id}"
```

---

#### T02.4: Add operation_kinds Field
**Duration**: 2 minutes  
**Tasks**:
- Add `operation_kinds: []` to all patterns
- Leave empty for now (to be populated later)
- Preserve all existing fields

**Update Logic**:
```python
for pattern in patterns:
    if 'operation_kinds' not in pattern:
        pattern['operation_kinds'] = []
```

---

#### T02.5: Update Metadata
**Duration**: 1 minute  
**Tasks**:
- Update `last_updated` timestamp
- Update `total_patterns` count if changed
- Add note about operation_kinds addition

---

#### T02.6: Write Updated YAML
**Duration**: 1 minute  
**Tasks**:
- Write updated structure to file
- Preserve formatting and comments
- Validate YAML syntax

---

#### T02.7: Validate Changes
**Duration**: 2 minutes  
**Tasks**:
- Verify all patterns have `doc_id`
- Verify all patterns have `operation_kinds` field
- Verify no patterns were lost
- Verify YAML is valid

**Validation**:
```python
# Verify all patterns have required fields
for pattern in patterns:
    assert 'doc_id' in pattern, f"Missing doc_id: {pattern['pattern_id']}"
    assert 'operation_kinds' in pattern, f"Missing operation_kinds: {pattern['pattern_id']}"
    assert 'pattern_id' in pattern
```

---

### Pattern for S02: UPDATE_PATTERN_INDEX

```yaml
pattern_id: PAT-UPDATE-REGISTRY-001
operation_kind: UPDATE_PATTERN_INDEX
steps:
  1_backup:
    - create_timestamped_backup
  2_analyze:
    - load_current_structure
    - identify_missing_fields
    - generate_migration_plan
  3_transform:
    - backfill_doc_ids
    - add_operation_kinds_field
    - preserve_existing_data
  4_update:
    - update_metadata
    - write_updated_yaml
  5_validate:
    - verify_all_required_fields
    - check_no_data_loss
    - validate_yaml_syntax
```

**Estimated**: 12 minutes (was 10, +2 for safety)

---

## STEP S03: Create PATTERN_ROUTING.yaml

### Task Breakdown

#### T03.1: Design Routing Structure
**Duration**: 3 minutes  
**Tasks**:
- Review OPERATION_KIND_REGISTRY.yaml for operation kinds
- Review PATTERN_INDEX.yaml for patterns
- Map which operations each pattern implements
- Design routing rules structure

**Structure**:
```yaml
version: 1.0.0
metadata:
  created: "2025-11-24"
  routing_strategy: operation_kind_to_pattern

routes:
  <OPERATION_KIND>:
    default_pattern: <PATTERN_ID>
    variants:
      - pattern_id: <PATTERN_ID>
        when:
          language: <LANGUAGE>
          context: <CONTEXT>
```

---

#### T03.2: Map Core Operations to Patterns
**Duration**: 4 minutes  
**Tasks**:
- Map PROCESS_PATCHES → PAT-PATCH-001
- Map SEARCH_FILES → PAT-SEARCH-001
- Map CREATE_FILE, SAVE_FILE → existing patterns
- Map RUN_TESTS → existing test patterns
- Leave unmapped operations as `null` or with comment

**Example**:
```yaml
routes:
  PROCESS_PATCHES:
    default_pattern: PAT-PATCH-001
    description: "Automated patch lifecycle management"
  
  SEARCH_FILES:
    default_pattern: PAT-SEARCH-001
    description: "Deep directory search"
  
  CREATE_FILE:
    default_pattern: PAT-ATOMIC-CREATE-001
    variants:
      - pattern_id: PAT-BATCH-CREATE-001
        when:
          file_count: ">3"
```

---

#### T03.3: Create YAML File
**Duration**: 2 minutes  
**Tasks**:
- Write YAML structure
- Add documentation comments
- Validate syntax

---

#### T03.4: Validate Routing Logic
**Duration**: 1 minute  
**Tasks**:
- Verify all referenced pattern_ids exist in PATTERN_INDEX
- Verify all operation_kinds exist in OPERATION_KIND_REGISTRY
- Check for circular references

---

### Pattern for S03: CREATE_ROUTING_FILE

```yaml
pattern_id: PAT-CREATE-ROUTING-001
operation_kind: CREATE_ROUTING_FILE
steps:
  1_design:
    - review_operation_kinds
    - review_patterns
    - map_relationships
  2_create:
    - write_routing_structure
    - add_documentation
    - handle_unmapped_operations
  3_validate:
    - verify_pattern_existence
    - verify_operation_kind_existence
    - check_routing_logic
```

**Estimated**: 10 minutes ✅

---

## STEP S04: Make PAT-PATCH-001 Compliant

### Task Breakdown

#### T04.1: Create .pattern.yaml Spec
**Duration**: 8 minutes  
**Tasks**:
- Read existing `.md` spec
- Extract key information
- Create YAML structure with required fields:
  - `doc_id`: DOC-PAT-PATCH-001
  - `pattern_id`: PAT-PATCH-001
  - `name`: patch_lifecycle
  - `version`: 1.0.0
  - `role`: spec
  - `operation_kinds`: [PROCESS_PATCHES, APPLY_PATCH, ARCHIVE_PATCH]
  - `schema_ref`: patterns/schemas/patch_lifecycle.schema.json
  - `executor_ref`: patterns/executors/patch_lifecycle_executor.py
- Write to `patterns/specs/patch_lifecycle.pattern.yaml`

---

#### T04.2: Create JSON Schema
**Duration**: 10 minutes  
**Tasks**:
- Define input schema for patch processing
- Required fields: operation_mode (process_all, check, apply, validate)
- Optional fields: patch_file, dry_run, repository_path
- Add `doc_id` field to schema
- Write to `patterns/schemas/patch_lifecycle.schema.json`

**Schema Template**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "doc_id": "DOC-PAT-PATCH-001",
  "title": "Patch Lifecycle Pattern",
  "type": "object",
  "required": ["operation_mode"],
  "properties": {
    "operation_mode": {
      "type": "string",
      "enum": ["process_all", "check", "apply", "validate", "dry_run"]
    },
    "patch_file": {
      "type": "string",
      "description": "Path to specific patch file"
    },
    "repository_path": {
      "type": "string",
      "default": "."
    },
    "dry_run": {
      "type": "boolean",
      "default": false
    }
  }
}
```

---

#### T04.3: Move & Update Executor
**Duration**: 5 minutes  
**Tasks**:
- Copy `scripts/process_patches.py` → `patterns/executors/patch_lifecycle_executor.py`
- Add DOC_LINK header at top:
  ```python
  # DOC_LINK: DOC-PAT-PATCH-001
  # Pattern: Patch Lifecycle Management
  # Version: 1.0.0
  ```
- Keep original in `scripts/` as wrapper/entry point
- Update imports if needed

---

#### T04.4: Create Test File
**Duration**: 7 minutes  
**Tasks**:
- Create `patterns/tests/test_patch_lifecycle_executor.py`
- Add DOC_LINK header
- Write basic tests:
  - Test patch discovery
  - Test patch status detection (applied vs unapplied)
  - Test dry-run mode
  - Test directory structure creation

**Test Template**:
```python
# DOC_LINK: DOC-PAT-PATCH-001
"""Tests for patch lifecycle management pattern."""

import pytest
from pathlib import Path
from patterns.executors.patch_lifecycle_executor import PatchManager

def test_patch_discovery():
    """Test recursive patch file discovery."""
    manager = PatchManager(".")
    patches = manager.discover_all_patches()
    assert isinstance(patches, list)

def test_patch_status_detection():
    """Test detection of applied vs unapplied patches."""
    # Test implementation
    pass

def test_dry_run_mode():
    """Test dry-run mode doesn't make changes."""
    # Test implementation
    pass
```

---

#### T04.5: Create Example Files
**Duration**: 5 minutes  
**Tasks**:
- Create directory: `patterns/examples/patch_lifecycle/`
- Create `instance_minimal.json`:
  ```json
  {
    "doc_id": "DOC-PAT-PATCH-001",
    "pattern_id": "PAT-PATCH-001",
    "operation_mode": "process_all",
    "repository_path": ".",
    "dry_run": false
  }
  ```
- Create `instance_check_specific.json`:
  ```json
  {
    "doc_id": "DOC-PAT-PATCH-001",
    "pattern_id": "PAT-PATCH-001",
    "operation_mode": "check",
    "patch_file": "patches/001-example.patch"
  }
  ```

---

#### T04.6: Move Documentation
**Duration**: 2 minutes  
**Tasks**:
- Move `patterns/specs/PAT-PATCH-001_patch_lifecycle_management.md` → `patterns/docs/`
- Update any references in other docs

---

### Pattern for S04: REFACTOR_PATTERN_COMPLIANCE

```yaml
pattern_id: PAT-MAKE-COMPLIANT-001
operation_kind: REFACTOR_PATTERN_COMPLIANCE
steps:
  1_create_spec:
    - read_existing_documentation
    - extract_key_metadata
    - create_pattern_yaml
    - add_doc_id_and_operation_kinds
  2_create_schema:
    - define_input_parameters
    - add_validation_rules
    - embed_doc_id
    - write_json_schema
  3_move_executor:
    - copy_to_patterns_executors
    - add_doc_link_header
    - update_imports
  4_create_tests:
    - create_test_file
    - add_doc_link_header
    - write_basic_tests
  5_create_examples:
    - create_example_directory
    - write_minimal_instance
    - write_variant_instances
  6_cleanup:
    - move_docs_to_patterns_docs
    - update_references
```

**Estimated**: 37 minutes (was 25, +12 for schema/tests/examples creation)

---

## STEP S05: Make PAT-SEARCH-001 Compliant

### Task Breakdown
(Similar to S04 but for deep_search pattern)

#### T05.1: Create .pattern.yaml Spec (6 min)
#### T05.2: Create JSON Schema (8 min)
#### T05.3: Move & Update Executor (5 min)
#### T05.4: Create Test File (6 min)
#### T05.5: Create Example Files (4 min)
#### T05.6: Move Documentation (1 min)

**Total**: 30 minutes (was 20, +10 for additional work)

---

## STEP S06: Register Patterns in PATTERN_INDEX.yaml

### Task Breakdown

#### T06.1: Prepare Pattern Entries
**Duration**: 3 minutes  
**Tasks**:
- Create entry for PAT-PATCH-001 with all required fields
- Create entry for PAT-SEARCH-001 with all required fields
- Ensure `doc_id`, `operation_kinds`, and all paths are correct

**Entry Template**:
```yaml
- pattern_id: PAT-PATCH-001
  doc_id: DOC-PAT-PATCH-001
  name: patch_lifecycle
  version: "1.0.0"
  status: stable
  category: infrastructure
  spec_path: patterns/specs/patch_lifecycle.pattern.yaml
  schema_path: patterns/schemas/patch_lifecycle.schema.json
  executor_path: patterns/executors/patch_lifecycle_executor.py
  test_path: patterns/tests/test_patch_lifecycle_executor.py
  example_dir: patterns/examples/patch_lifecycle/
  operation_kinds:
    - PROCESS_PATCHES
    - APPLY_PATCH
    - ARCHIVE_PATCH
  created: "2025-11-24"
  last_updated: "2025-11-24"
```

---

#### T06.2: Update PATTERN_INDEX.yaml
**Duration**: 2 minutes  
**Tasks**:
- Backup current file
- Add both pattern entries
- Update metadata (total_patterns count)
- Update last_updated timestamp

---

#### T06.3: Validate Entries
**Duration**: 2 minutes  
**Tasks**:
- Verify all paths exist
- Verify YAML is valid
- Verify no duplicate pattern_ids or doc_ids
- Check operation_kinds exist in registry

---

### Pattern for S06: UPDATE_PATTERN_INDEX

```yaml
pattern_id: PAT-REGISTER-PATTERN-001
operation_kind: UPDATE_PATTERN_INDEX
steps:
  1_prepare:
    - gather_pattern_metadata
    - format_entries
    - verify_paths_exist
  2_update:
    - backup_current_index
    - add_new_entries
    - update_metadata
  3_validate:
    - verify_yaml_syntax
    - check_no_duplicates
    - verify_operation_kinds_exist
    - verify_all_paths_exist
```

**Estimated**: 7 minutes (was 10, optimized)

---

## STEP S07: Create PATTERN_DIR_CHECK.ps1 Validation Script

### Task Breakdown

#### T07.1: Design Validation Architecture
**Duration**: 5 minutes  
**Tasks**:
- Review PAT-CHECK-001 requirements (Sections 1-8)
- Design check function structure
- Design reporting format (JSON)
- Plan validation sequence

---

#### T07.2: Implement Directory Structure Checks (Section 1)
**Duration**: 5 minutes  
**Tasks**:
- Check `patterns/` exists
- Check required subdirectories exist:
  - `patterns/registry/`
  - `patterns/specs/`
  - `patterns/schemas/`
  - `patterns/executors/`
  - `patterns/examples/`
  - `patterns/tests/`

**Code**:
```powershell
function Test-DirectoryStructure {
    $results = @()
    
    $requiredDirs = @(
        "patterns",
        "patterns/registry",
        "patterns/specs",
        "patterns/schemas",
        "patterns/executors",
        "patterns/examples",
        "patterns/tests"
    )
    
    foreach ($dir in $requiredDirs) {
        $exists = Test-Path $dir
        $results += [PSCustomObject]@{
            RequirementId = "PAT-CHECK-001-001"
            Check = "Directory exists: $dir"
            Status = if ($exists) { "PASS" } else { "FAIL" }
            Details = if ($exists) { "Found" } else { "Missing" }
        }
    }
    
    return $results
}
```

---

#### T07.3: Implement PATTERN_INDEX.yaml Checks (Section 2)
**Duration**: 8 minutes  
**Tasks**:
- Check file exists and is valid YAML
- Check all required fields present in each pattern
- Check doc_id format
- Check all referenced paths exist

---

#### T07.4: Implement Spec File Checks (Section 3)
**Duration**: 5 minutes  
**Tasks**:
- For each pattern in index:
  - Verify spec_path exists
  - Parse spec file
  - Verify has doc_id matching index
  - Verify has pattern_id matching index

---

#### T07.5: Implement Schema/Executor/Test/Example Checks (Sections 4-7)
**Duration**: 10 minutes  
**Tasks**:
- Similar checks for schema, executor, test, example paths
- Verify DOC_LINK headers in code files
- Verify doc_id consistency

---

#### T07.6: Implement Cross-Artifact Consistency Check (Section 8)
**Duration**: 4 minutes  
**Tasks**:
- For each pattern:
  - Collect all doc_ids from all artifacts
  - Verify they all match
  - Report any mismatches

---

#### T07.7: Implement Reporting & Summary
**Duration**: 3 minutes  
**Tasks**:
- Collect all check results
- Generate summary counts
- Output JSON format
- Set exit code (0 = success, 1 = failures)

**Output Format**:
```json
{
  "timestamp": "2025-11-24T16:34:08Z",
  "total_checks": 127,
  "passed": 125,
  "failed": 2,
  "status": "FAIL",
  "details": [
    {
      "requirement_id": "PAT-CHECK-001-020",
      "check": "Spec file exists: atomic_create.pattern.yaml",
      "status": "PASS"
    }
  ],
  "summary": {
    "compliant_patterns": 22,
    "non_compliant_patterns": 2
  }
}
```

---

### Pattern for S07: CREATE_VALIDATION_SCRIPT

```yaml
pattern_id: PAT-CREATE-VALIDATOR-001
operation_kind: CREATE_VALIDATION_SCRIPT
steps:
  1_design:
    - review_requirements_spec
    - design_check_architecture
    - plan_reporting_format
  2_implement_checks:
    - directory_structure_checks
    - pattern_index_checks
    - spec_file_checks
    - schema_checks
    - executor_checks
    - test_checks
    - example_checks
    - cross_artifact_consistency
  3_reporting:
    - collect_results
    - generate_summary
    - output_json
    - set_exit_code
  4_test:
    - test_against_compliant_pattern
    - test_against_non_compliant
    - verify_error_detection
```

**Estimated**: 40 minutes (was 30, +10 for comprehensive validation)

---

## STEP S08: Create OPK Miner Script

### Task Breakdown

#### T08.1: Design Mining Strategy
**Duration**: 3 minutes  
**Tasks**:
- Define scan targets (logs/, specs/, master_plan/)
- Define extraction patterns (verbs, action phrases)
- Design frequency counting approach
- Design output format

---

#### T08.2: Implement File Scanner
**Duration**: 5 minutes  
**Tasks**:
- Recursive directory traversal
- File type filtering (.md, .txt, .yaml)
- Text extraction

---

#### T08.3: Implement Phrase Extraction
**Duration**: 7 minutes  
**Tasks**:
- Regex patterns for action verbs
- Extract phrases from bullet lists
- Extract from step descriptions
- Count frequency

**Patterns**:
- Lines starting with verbs: `^(Create|Update|Delete|Run|Execute|Generate).*`
- Bullet list items: `^\s*[-*]\s*(.+)`
- Step descriptions: `Step \d+: (.+)`

---

#### T08.4: Implement Filtering & Ranking
**Duration**: 3 minutes  
**Tasks**:
- Filter out already-registered operation kinds
- Rank by frequency
- Remove duplicates
- Normalize phrases

---

#### T08.5: Generate Output
**Duration**: 2 minutes  
**Tasks**:
- Format as JSON
- Include phrase, count, source files
- Sort by frequency

**Output Format**:
```json
{
  "scan_date": "2025-11-24",
  "sources_scanned": ["logs/", "specs/", "master_plan/"],
  "total_phrases": 487,
  "candidates": [
    {
      "phrase": "create file",
      "count": 42,
      "normalized": "CREATE_FILE",
      "already_registered": true,
      "sources": ["logs/session1.md", "specs/pattern.md"]
    },
    {
      "phrase": "validate changes",
      "count": 27,
      "normalized": "VALIDATE_CHANGES",
      "already_registered": false,
      "sources": ["master_plan/phase1.md"]
    }
  ]
}
```

---

### Pattern for S08: CREATE_ANALYSIS_SCRIPT

```yaml
pattern_id: PAT-CREATE-MINER-001
operation_kind: CREATE_ANALYSIS_SCRIPT
steps:
  1_design:
    - define_scan_targets
    - design_extraction_patterns
    - plan_output_format
  2_implement_scanner:
    - recursive_file_traversal
    - file_type_filtering
    - text_extraction
  3_implement_extraction:
    - verb_pattern_matching
    - phrase_extraction
    - frequency_counting
  4_filter_rank:
    - exclude_registered_opks
    - rank_by_frequency
    - normalize_phrases
  5_output:
    - format_json
    - write_candidates_file
```

**Estimated**: 20 minutes ✅

---

## STEP S09: Create OPK Normalization Pattern

### Task Breakdown

#### T09.1: Create Pattern Spec
**Duration**: 4 minutes  
**Tasks**:
- Create `opk_normalization.pattern.yaml`
- Add doc_id: DOC-PAT-OPK-NORM-001
- Add operation_kinds: [NORMALIZE_OPERATION_KINDS]
- Include strict normalization prompt as template

---

#### T09.2: Create Schema
**Duration**: 4 minutes  
**Tasks**:
- Define input: array of raw phrases
- Define output: OPERATION_KIND_REGISTRY format
- Add validation rules

---

#### T09.3: Create Executor
**Duration**: 4 minutes  
**Tasks**:
- Create Python script that invokes LLM
- Include strict prompt from `assistant_responses_operation_kinds.md`
- Handle input/output formatting

---

#### T09.4: Create Tests
**Duration**: 2 minutes  
**Tasks**:
- Test with sample phrases
- Verify output format

---

#### T09.5: Create Examples
**Duration**: 1 minute  
**Tasks**:
- Create example input/output pair

---

### Pattern for S09: CREATE_PATTERN_SPEC

```yaml
pattern_id: PAT-CREATE-PATTERN-001
operation_kind: CREATE_PATTERN_SPEC
steps:
  1_spec:
    - create_pattern_yaml
    - add_doc_id
    - add_operation_kinds
    - include_templates
  2_schema:
    - define_input_output
    - add_validation
  3_executor:
    - create_implementation
    - add_doc_link
  4_tests:
    - create_test_file
    - write_tests
  5_examples:
    - create_example_instances
```

**Estimated**: 15 minutes ✅

---

## STEP S10: Register OPK Normalization Pattern

### Task Breakdown

#### T10.1: Add to PATTERN_INDEX.yaml
**Duration**: 2 minutes  
**Tasks**:
- Create entry for PAT-OPK-NORM-001
- Add all required fields

---

#### T10.2: Add to PATTERN_ROUTING.yaml
**Duration**: 1 minute  
**Tasks**:
- Map NORMALIZE_OPERATION_KINDS → PAT-OPK-NORM-001

---

#### T10.3: Validate
**Duration**: 2 minutes  
**Tasks**:
- Run PATTERN_DIR_CHECK.ps1
- Verify pattern is compliant

---

### Pattern for S10: UPDATE_PATTERN_INDEX

(Reuse pattern from S06)

**Estimated**: 5 minutes ✅

---

## EXECUTION PATTERNS SUMMARY

### Pattern 1: CREATE_REGISTRY_FILE
**Used in**: S01, S03  
**Steps**: Research → Define → Create → Validate  
**Duration**: 10-15 minutes

### Pattern 2: UPDATE_PATTERN_INDEX  
**Used in**: S02, S06, S10  
**Steps**: Backup → Analyze → Transform → Update → Validate  
**Duration**: 5-12 minutes

### Pattern 3: REFACTOR_PATTERN_COMPLIANCE
**Used in**: S04, S05  
**Steps**: Create spec → Schema → Move executor → Tests → Examples → Cleanup  
**Duration**: 30-37 minutes

### Pattern 4: CREATE_VALIDATION_SCRIPT
**Used in**: S07  
**Steps**: Design → Implement checks → Reporting → Test  
**Duration**: 40 minutes

### Pattern 5: CREATE_ANALYSIS_SCRIPT
**Used in**: S08  
**Steps**: Design → Scanner → Extraction → Filter → Output  
**Duration**: 20 minutes

### Pattern 6: CREATE_PATTERN_SPEC
**Used in**: S09  
**Steps**: Spec → Schema → Executor → Tests → Examples  
**Duration**: 15 minutes

---

## TOTAL TIME ESTIMATES (Updated)

```
S01: 15 min  (CREATE_REGISTRY_FILE)
S02: 12 min  (UPDATE_PATTERN_INDEX)
S03: 10 min  (CREATE_ROUTING_FILE)
S04: 37 min  (REFACTOR_PATTERN_COMPLIANCE)
S05: 30 min  (REFACTOR_PATTERN_COMPLIANCE)
S06:  7 min  (UPDATE_PATTERN_INDEX)
S07: 40 min  (CREATE_VALIDATION_SCRIPT)
S08: 20 min  (CREATE_ANALYSIS_SCRIPT) [DEFERRABLE]
S09: 15 min  (CREATE_PATTERN_SPEC) [DEFERRABLE]
S10:  5 min  (UPDATE_PATTERN_INDEX) [DEFERRABLE]

Critical Path (S01-S07): 151 minutes (2.5 hours)
Full Execution (S01-S10): 191 minutes (3.2 hours)
```

---

## RECOMMENDED APPROACH

**Option B - Critical Path Execution:**
1. Execute S01-S07 in sequence (151 min / 2.5 hours)
2. Skip to S11 (validation)
3. Defer S08-S10 to future session

This keeps us on the original 2.5-hour estimate while delivering all critical infrastructure.

---

**Status**: ✅ TASK ANALYSIS COMPLETE  
**Patterns Developed**: 6 execution patterns  
**Ready for Execution**: YES
