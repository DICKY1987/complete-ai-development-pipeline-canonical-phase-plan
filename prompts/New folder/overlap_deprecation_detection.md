# Overlapping Implementations & Deprecated Code Detection Prompt

## Mission
Identify overlapping implementations, deprecated code, and redundant functionality across the codebase. Deliver specific recommendations for consolidation and removal.

## Detection Framework

### Phase 1: Overlap Detection

#### 1.1 Functional Overlap
Scan for multiple implementations of the same behavior:
- **Duplicate functions**: Same logic, different names/locations
- **Parallel implementations**: Same feature in multiple modules
- **Copy-paste code**: Similar blocks with minor variations
- **Competing patterns**: Multiple ways to achieve the same goal
- **Redundant utilities**: Helper functions that do the same thing

**Detection Signals**:
- Similar function signatures with different names
- Identical or near-identical code blocks (>80% similarity)
- Same imports and dependencies in different files
- Similar test patterns for different functions
- Multiple files in different locations solving same problem

#### 1.2 Module/Package Overlap
Identify competing modules:
- **Legacy vs new**: Old implementation alongside replacement
- **Forked implementations**: Variations that diverged from common origin
- **Vendor lock-in duplicates**: Multiple implementations for different providers
- **Test vs production**: Duplicate logic in test utilities
- **Migration artifacts**: Both old and new paths coexisting

**Detection Signals**:
- Directory names like `old_*`, `legacy_*`, `v1_*`, `deprecated_*`
- Import paths with version indicators
- Similar module structures in different locations
- README/docs mentioning "new" or "replacement" for existing code

#### 1.3 Configuration Overlap
Find redundant configuration:
- **Duplicate settings**: Same config in multiple files
- **Conflicting defaults**: Different default values for same setting
- **Environment-specific duplicates**: Dev/staging/prod configs with mostly identical content
- **Schema duplication**: Same data models in different formats (JSON/YAML/Python)

### Phase 2: Deprecation Detection

#### 2.1 Explicit Deprecation Markers
Search for:
```python
# Deprecation patterns
@deprecated
@deprecated(reason="...", version="...")
# DEPRECATED:
# TODO: Remove this after...
warnings.warn("deprecated", DeprecationWarning)
```

```javascript
/** @deprecated Use ... instead */
// DEPRECATED
console.warn('DEPRECATED:')
```

#### 2.2 Implicit Deprecation Signals
Look for:
- **Unused code**: Functions/classes with zero call sites
- **Import isolation**: Modules never imported elsewhere
- **Dead branches**: Git branches that merged but left old code
- **TODO removals**: Comments like "TODO: delete after migration"
- **Version markers**: Code marked for specific version removal
- **Last modified dates**: Files untouched for >1 year with newer alternatives

#### 2.3 Documentation Deprecation
Check documentation for:
- "This is deprecated" / "Use X instead"
- Changelog entries marking features as deprecated
- Migration guides away from certain APIs
- ADRs (Architecture Decision Records) deprecating approaches

#### 2.4 Dependency Deprecation
Identify deprecated dependencies:
- Packages with deprecation warnings
- Libraries with security vulnerabilities
- Abandoned projects (no updates >2 years)
- Superseded by newer packages

### Phase 3: Impact Analysis

For each finding, determine:

#### 3.1 Usage Analysis
```
Finding ID: OVLP-XXX or DEPR-XXX
Type: [Duplicate Function | Overlapping Module | Deprecated API | Unused Code]

Current Usage:
- Active call sites: [count and locations]
- Import references: [count and locations]
- Test coverage: [count and locations]
- External dependencies: [other code that depends on this]

Risk Level: [Critical | High | Medium | Low | Safe]
- Critical: Actively used in production
- High: Used in multiple modules
- Medium: Used in limited scope
- Low: Used only in tests
- Safe: No active references found
```

#### 3.2 Overlap Relationship Mapping
```
Overlap Group: OG-XXX

Implementations:
1. [Location 1] - [Description] - [Status: Active/Deprecated/Unknown]
   - Lines of code: XXX
   - First commit: YYYY-MM-DD
   - Last modified: YYYY-MM-DD
   - Call sites: XXX

2. [Location 2] - [Description] - [Status: Active/Deprecated/Unknown]
   - Lines of code: XXX
   - First commit: YYYY-MM-DD
   - Last modified: YYYY-MM-DD
   - Call sites: XXX

Recommended Keeper: [Implementation #X]
Reason: [Why this one - most complete, best tested, actively maintained, etc.]

Items to Deprecate/Remove: [Implementation #Y, #Z]
Reason: [Why remove these - older, less complete, not tested, etc.]
```

## Detection Methodology

### Automated Scans

#### Scan 1: Code Similarity Detection
```bash
# Find similar code blocks
- Compare function bodies using diff/similarity metrics
- Flag >80% similarity as duplicate
- Flag >60% similarity as potential overlap
```

#### Scan 2: Import Graph Analysis
```bash
# Build import dependency graph
- Identify modules with zero incoming imports (unused)
- Identify circular dependencies (refactoring candidates)
- Find parallel import paths (competing implementations)
```

#### Scan 3: Pattern Matching
```bash
# Search for explicit markers
grep -r "deprecated" --include="*.py" --include="*.js" --include="*.md"
grep -r "TODO.*remove" --include="*.py" --include="*.js"
grep -r "legacy" --include="*.py" --include="*.js"
grep -r "old_" --include="*.py" --include="*.js"
```

#### Scan 4: Git History Analysis
```bash
# Analyze file history
- Find files not modified in >1 year
- Identify files with "deprecated" in commit messages
- Locate renamed/moved files (possible duplicates)
```

#### Scan 5: Dead Code Detection
```bash
# Static analysis for unused code
- Functions never called
- Classes never instantiated
- Modules never imported
- Commented-out code blocks >50 lines
```

## Output Format

### Executive Summary
```
Overlap & Deprecation Analysis Report
Generated: [timestamp]

Findings Overview:
- Total overlapping implementations: X
- Deprecated code items: X
- Unused/dead code items: X
- Total lines of code affected: XXX
- Estimated cleanup effort: X hours
- Risk distribution: [Critical: X, High: X, Medium: X, Low: X, Safe: X]
```

### Detailed Findings

#### Section 1: Overlapping Implementations
```
OVLP-001: Duplicate JSON Schema Validation
Priority: High
Risk Level: Medium

Implementations Found:
1. core/validation/schema_validator.py (245 lines)
   - Status: Active, well-tested
   - Call sites: 12 locations
   - Last modified: 2024-11-15
   - Features: Full JSON Schema Draft 7, custom validators

2. utils/json_utils.py::validate_json() (87 lines)
   - Status: Active, limited tests
   - Call sites: 3 locations
   - Last modified: 2023-06-20
   - Features: Basic validation only

Overlap Analysis:
- Functional overlap: 85%
- Code similarity: 45%
- Feature parity: Implementation #1 is superset

RECOMMENDATION:
  Title: Consolidate to core/validation/schema_validator.py

  Actions:
  1. Migrate 3 call sites from utils/json_utils.py to schema_validator
  2. Add deprecation warning to json_utils.validate_json()
  3. Update docs to reference schema_validator as canonical
  4. Remove json_utils.validate_json() in next major version

  Migration Steps:
  1. [File 1]: Replace utils.json_utils.validate_json() → core.validation.schema_validator.validate()
  2. [File 2]: Replace utils.json_utils.validate_json() → core.validation.schema_validator.validate()
  3. [File 3]: Replace utils.json_utils.validate_json() → core.validation.schema_validator.validate()

  Effort: 2 hours
  Risk: Low (schema_validator has broader test coverage)

  Expected Benefits:
  - Remove 87 lines of duplicate code
  - Reduce maintenance burden (1 implementation vs 2)
  - Improve consistency across codebase
```

#### Section 2: Deprecated Code
```
DEPR-001: Legacy Pipeline Module
Priority: Critical
Risk Level: High

Location: src/pipeline/**
Status: Explicitly deprecated (see MIGRATION_GUIDE.md)

Deprecation Evidence:
- @deprecated decorator on all public functions
- README.md states "DO NOT USE - migrated to core.*"
- Last modified: 2024-03-10
- Deprecation date: 2024-06-01 (6 months ago)

Current Usage:
- Active imports: 5 locations (CRITICAL!)
- Test references: 12 tests still using old API
- Documentation: 3 docs still reference old module

RECOMMENDATION:
  Title: Complete migration from src/pipeline to core

  Migration Required:
  1. [file1.py:45] src.pipeline.db → core.state.db
  2. [file2.py:12] src.pipeline.executor → core.engine.executor
  3. [file3.py:78] src.pipeline.scheduler → core.engine.scheduler
  4. [file4.py:34] src.pipeline.config → core.config
  5. [file5.py:90] src.pipeline.models → core.models

  Test Migration:
  - Migrate 12 tests to use core.* imports
  - Verify behavior parity
  - Remove old test fixtures

  Documentation Updates:
  - Update quickstart.md (lines 45-67)
  - Update API_REFERENCE.md (lines 120-180)
  - Update CONTRIBUTING.md (lines 34-40)

  Final Removal:
  - After all migrations, delete src/pipeline/ entirely
  - Remove from .gitignore exclusions
  - Update CHANGELOG.md

  Effort: 6 hours
  Risk: High (requires thorough testing)
  Testing: Run full test suite + manual smoke tests

  Dependencies: None (migration path documented)
```

#### Section 3: Unused/Dead Code
```
DEAD-001: Unused Utility Functions
Priority: Low
Risk Level: Safe

Location: utils/string_helpers.py
Functions: to_camel_case(), to_snake_case(), slugify()

Usage Analysis:
- Import references: 0
- Call sites: 0 (confirmed via grep + AST analysis)
- Git history: Not modified since 2023-01-15
- Tests: Unit tests exist but function never used

RECOMMENDATION:
  Title: Remove unused string utility functions

  Actions:
  1. Delete to_camel_case(), to_snake_case(), slugify() from utils/string_helpers.py
  2. Remove corresponding tests from tests/utils/test_string_helpers.py
  3. If file becomes empty, delete entire utils/string_helpers.py

  Effort: 30 minutes
  Risk: Safe (zero usage confirmed)

  Expected Benefits:
  - Remove 120 lines of dead code
  - Remove 85 lines of dead tests
  - Reduce cognitive load when browsing utils/
```

### Consolidation Roadmap

#### Phase 1: Safe Removals (Week 1)
**Risk: Safe | Effort: 2-4 hours**
- Remove unused/dead code with zero call sites
- Delete empty or obsolete test files
- Clean up commented-out code blocks

Items:
- [DEAD-001, DEAD-002, DEAD-003...]

#### Phase 2: Overlap Consolidation (Week 2-3)
**Risk: Low-Medium | Effort: 8-12 hours**
- Consolidate duplicate implementations
- Migrate to canonical implementation
- Add deprecation warnings

Items:
- [OVLP-001, OVLP-002, OVLP-003...]

#### Phase 3: Deprecation Cleanup (Week 4-6)
**Risk: Medium-High | Effort: 16-24 hours**
- Complete migrations away from deprecated code
- Update all call sites
- Remove deprecated modules
- Update documentation

Items:
- [DEPR-001, DEPR-002, DEPR-003...]

#### Phase 4: Verification (Week 7)
**Risk: N/A | Effort: 4-6 hours**
- Run full test suite
- Manual regression testing
- Update dependency graphs
- Generate before/after metrics

## Analysis Instructions

### 1. Be Conservative
- **Don't assume**: If unsure whether code is used, mark as "needs investigation"
- **Verify zero usage**: Use multiple methods (grep, AST analysis, import graphs)
- **Check tests**: Code used only in tests may still be valuable

### 2. Provide Evidence
- Include file paths and line numbers
- Show code snippets demonstrating overlap
- List all call sites and imports
- Reference git history when relevant

### 3. Assess Risk Accurately
- **Critical**: Production code, user-facing APIs
- **High**: Used in multiple modules, core functionality
- **Medium**: Limited usage, good test coverage exists
- **Low**: Test-only usage, well-isolated
- **Safe**: Zero usage confirmed, no external dependencies

### 4. Consider Context
- Check if "duplicate" code has subtle but important differences
- Verify that "newer" implementation has feature parity
- Look for migration guides or ADRs explaining the situation
- Respect intentional redundancy (e.g., vendored code, platform-specific implementations)

### 5. Quantify Impact
- Lines of code to remove
- Number of files affected
- Test coverage implications
- Documentation updates needed
- Estimated effort (hours)

## Success Criteria

Analysis is complete when:
- ✅ All duplicate implementations are identified and mapped
- ✅ All deprecated code is catalogued with usage data
- ✅ All unused code is verified with zero references
- ✅ Each finding has a specific migration path
- ✅ Risk levels are accurately assessed
- ✅ Consolidation roadmap is sequenced by risk/effort
- ✅ Before/after metrics are calculated

## Begin Analysis

### Step 1: Quick Scan (30 minutes)
```bash
# Find obvious candidates
1. Search for "deprecated", "legacy", "old_" in code and docs
2. List directories: legacy/, old/, deprecated/, archive/
3. Find files not modified in >1 year
4. Grep for TODO removal comments
```

### Step 2: Deep Analysis (2-4 hours)
```bash
# Detailed overlap detection
1. Build import dependency graph
2. Run code similarity analysis on all Python/JS files
3. Identify parallel module structures
4. Analyze function signature similarities
5. Map configuration files for duplicates
```

### Step 3: Usage Verification (1-2 hours)
```bash
# Confirm usage/non-usage
1. For each candidate, search all call sites
2. Check test files for references
3. Verify import statements
4. Review git blame for recent activity
```

### Step 4: Report Generation (1 hour)
```bash
# Compile findings
1. Sort by priority (Critical → Safe)
2. Group related items
3. Calculate total impact metrics
4. Generate phased roadmap
```

## Example Query Patterns

### Finding Overlaps
```bash
# Similar function names
grep -r "def validate_" --include="*.py" | sort

# Similar imports in different files
find . -name "*.py" -exec grep -l "import json" {} \; | xargs grep -h "import"

# Duplicate test patterns
grep -r "def test_validation" tests/
```

### Finding Deprecated Code
```bash
# Explicit markers
grep -rn "@deprecated\|DEPRECATED\|TODO.*remove" --include="*.py" --include="*.js"

# Legacy paths
find . -type d -name "*legacy*" -o -name "*old*" -o -name "*deprecated*"

# Import path violations (if CI standards exist)
grep -r "from src.pipeline" --include="*.py"
grep -r "from MOD_ERROR_PIPELINE" --include="*.py"
```

### Finding Dead Code
```bash
# Unused functions (requires AST or static analysis tool)
# Manual approach: search for function definitions, then search for calls
grep -r "def my_function" --include="*.py"  # definition
grep -r "my_function(" --include="*.py"     # usage
```

Generate the complete overlap and deprecation analysis report now.
