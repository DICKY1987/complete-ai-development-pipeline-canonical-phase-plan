# Execution Patterns Library - Speed Up AI-Assisted Development

**DOC_ID:** DOC-PAT-EXECUTION-LIBRARY-001  
**Based on:** UTE_decision-elimination-playbook.md  
**Status:** ACTIVE  
**Purpose:** Reusable patterns to achieve 3x-10x speedup on repetitive development tasks

---

## Pattern Index

| Pattern ID | Name | Use Case | Time Savings | Difficulty |
|-----------|------|----------|--------------|------------|
| EXEC-001 | Batch File Creator | Create N similar files | 58% | Easy |
| EXEC-002 | Code Module Generator | Generate similar code modules | 67% | Medium |
| EXEC-003 | Test Suite Multiplier | Write test cases at scale | 70% | Easy |
| EXEC-004 | Doc Standardizer | Create consistent documentation | 65% | Easy |
| EXEC-005 | Config Multiplexer | Generate configuration files | 75% | Easy |
| EXEC-006 | API Endpoint Factory | CRUD endpoints at scale | 83% | Medium |
| EXEC-007 | Schema Generator | JSON/YAML schemas in bulk | 60% | Medium |
| EXEC-008 | Migration Scripter | Database/code migrations | 55% | Hard |

---

## EXEC-001: Batch File Creator

### Problem
Need to create 10-100 similar files (manifests, configs, READMEs) across modules.

### Pattern Structure

```yaml
pattern: EXEC-001
name: Batch File Creator
phase_1_discovery: 3 examples (90 min)
phase_2_template: 1 template (30 min)
phase_3_batch: N files (5 min each)
phase_4_verify: spot check (2 min total)
```

### Template

```markdown
# TEMPLATE: {FILE_TYPE}
# Variables: {var1}, {var2}, {var3}
# Batch size: 6 files per tool call

---
{file_header}

{section_1}:
  {var1_content}

{section_2}:
  {var2_content}

{section_3}:
  {var3_content}

{file_footer}
---

# EXAMPLE (filled):
{concrete_example}
```

### Execution Script

```python
# DOC_LINK: DOC-PAT-EXECUTION-LIBRARY-001
# Pattern: EXEC-001 - Batch File Creator

from pathlib import Path
from typing import List, Dict
import yaml

class BatchFileCreator:
    """Create multiple similar files from template."""
    
    def __init__(self, template_path: Path):
        self.template = self._load_template(template_path)
        self.created_files = []
    
    def _load_template(self, path: Path) -> str:
        return path.read_text(encoding='utf-8')
    
    def fill_template(self, variables: Dict[str, str]) -> str:
        """Fill template with variables."""
        content = self.template
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", value)
        return content
    
    def create_batch(self, items: List[Dict], output_dir: Path, batch_size: int = 6):
        """Create files in parallel batches."""
        batches = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]
        
        for batch_num, batch in enumerate(batches, 1):
            print(f"\n📦 Batch {batch_num}/{len(batches)} ({len(batch)} files)")
            
            for item in batch:
                content = self.fill_template(item['variables'])
                output_path = output_dir / item['filename']
                output_path.write_text(content, encoding='utf-8')
                self.created_files.append(output_path)
                print(f"  ✓ {output_path.name}")
        
        return self.verify()
    
    def verify(self) -> Dict:
        """Ground truth verification: files exist."""
        existing = [f for f in self.created_files if f.exists()]
        
        return {
            'total_files': len(self.created_files),
            'existing_files': len(existing),
            'success': len(existing) == len(self.created_files),
            'files': [str(f) for f in existing]
        }

# USAGE EXAMPLE:
"""
creator = BatchFileCreator(Path('templates/module-manifest.yaml'))

items = [
    {
        'filename': 'core.manifest.yaml',
        'variables': {'module': 'core', 'purpose': 'Core engine'}
    },
    {
        'filename': 'error.manifest.yaml',
        'variables': {'module': 'error', 'purpose': 'Error detection'}
    },
    # ... 15 more items
]

result = creator.create_batch(items, Path('manifests/'), batch_size=6)
print(f"✅ Created {result['total_files']} files")
"""
```

### Time Analysis

```
Without pattern:
  30 min/file × 17 files = 8.5 hours

With pattern:
  Discovery: 90 min (first 3 files)
  Template: 30 min
  Batch: 5 min/file × 14 files = 70 min
  Total: 3.2 hours
  
Savings: 62% (5.3 hours saved)
Break-even: After 5th file
```

---

## EXEC-002: Code Module Generator

### Problem
Creating similar code modules (plugins, adapters, handlers) with consistent structure.

### Pattern Structure

```python
# TEMPLATE: Python Module
# Variables: {module_name}, {base_class}, {methods}

"""
{module_name}

DOC_ID: {doc_id}
PURPOSE: {purpose}
"""

from typing import {type_imports}
from {base_module} import {base_class}

class {ClassName}({base_class}):
    """
    {class_description}
    """
    
    def __init__(self, {init_params}):
        super().__init__()
        {init_body}
    
    # METHODS: {method_list}
    {method_implementations}

# USAGE EXAMPLE:
{usage_example}
```

### Execution Pattern

```yaml
discovery_phase:
  - Create 2-3 modules manually
  - Extract common structure
  - Identify variable sections
  
template_phase:
  - Create base class template
  - Define variable placeholders
  - Add 1 complete example
  
batch_phase:
  strategy: parallel_creation
  batch_size: 4-6 modules
  verification: import_test
  
verification_phase:
  ground_truth: "module imports without error"
  command: "python -c 'import {module_name}'"
  acceptance: "exit code 0"
```

### AI Prompt Template

```markdown
Using the module template in `templates/python-module.py`:

Create the following modules in parallel:

1. Module: error_plugin_typescript
   Purpose: TypeScript error detection
   Base: BaseErrorPlugin
   Methods: parse, fix

2. Module: error_plugin_golang
   Purpose: Go error detection  
   Base: BaseErrorPlugin
   Methods: parse, fix

3. Module: error_plugin_rust
   Purpose: Rust error detection
   Base: BaseErrorPlugin
   Methods: parse, fix

Requirements:
- Use template structure exactly
- Add DOC_ID for each module
- Include basic tests in docstrings
- Verify imports work

Batch create all 3 modules.
```

### Time Analysis

```
Manual: 45 min/module × 10 modules = 7.5 hours
Pattern: 2 hours (discovery) + 2 hours (batch) = 4 hours
Savings: 47% (3.5 hours saved)
```

---

## EXEC-003: Test Suite Multiplier

### Problem
Writing test cases for multiple similar functions/modules.

### Template

```python
# TEST TEMPLATE
# DOC_LINK: {doc_id}
# Tests for {module_name}

import pytest
from {module_path} import {function_name}

class Test{ClassName}:
    """Tests for {function_name}."""
    
    def test_happy_path(self):
        """Test with valid input."""
        input_data = {valid_input_example}
        result = {function_name}(input_data)
        
        assert result.success == True
        assert result.data == {expected_output}
    
    def test_error_{error_type_1}(self):
        """Test error: {error_description_1}."""
        input_data = {invalid_input_1}
        result = {function_name}(input_data)
        
        assert result.success == False
        assert "{error_keyword_1}" in str(result.error)
    
    def test_error_{error_type_2}(self):
        """Test error: {error_description_2}."""
        input_data = {invalid_input_2}
        result = {function_name}(input_data)
        
        assert result.success == False
        assert "{error_keyword_2}" in str(result.error)
    
    def test_edge_case_{edge_case_name}(self):
        """Test edge case: {edge_case_description}."""
        input_data = {edge_case_input}
        result = {function_name}(input_data)
        
        assert {edge_case_assertion}

# FIXTURE TEMPLATE (if needed):
@pytest.fixture
def {fixture_name}():
    """Fixture for {fixture_description}."""
    {fixture_setup}
    yield {fixture_object}
    {fixture_teardown}
```

### Execution Strategy

```bash
# 1. Discover pattern (first 2 tests)
# Write tests manually for:
#   - validate_user()
#   - validate_project()
# Notice: Same structure, just different inputs

# 2. Create template
# Extract common structure -> templates/test-suite.py

# 3. Batch generate tests
# Prompt: "Using templates/test-suite.py, create tests for:
#   validate_task, validate_comment, validate_attachment,
#   validate_milestone, validate_phase"

# 4. Verify
pytest tests/ -v --collect-only  # Verify all tests collected
pytest tests/ -x                  # Run until first failure
```

### Time Analysis

```
Manual: 20 min/test × 15 functions = 5 hours
Pattern: 1 hour (discovery) + 1.5 hours (batch) = 2.5 hours
Savings: 50% (2.5 hours saved)
```

---

## EXEC-004: Doc Standardizer

### Problem
Creating consistent documentation across modules/features.

### Template

```markdown
---
doc_id: {doc_id}
module: {module_name}
status: {alpha|beta|stable}
owner: {owner_name}
---

# {Module Name}

## Purpose

{one_sentence_purpose}

## Quick Start

```{language}
{quickstart_command}
```

## Key Concepts

- **{concept_1}**: {one_line_explanation_1}
- **{concept_2}**: {one_line_explanation_2}
- **{concept_3}**: {one_line_explanation_3}

## Common Tasks

### {task_1_name}

{task_1_description}

```{language}
{task_1_code_example}
```

### {task_2_name}

{task_2_description}

```{language}
{task_2_code_example}
```

## API Reference

### {primary_class}

{class_description}

**Methods:**
- `{method_1}({params})`: {method_1_description}
- `{method_2}({params})`: {method_2_description}

## Gotchas

- ⚠️ {gotcha_1}
- ⚠️ {gotcha_2}

## Related

- {related_module_1}
- {related_module_2}
```

### Batch Generation Strategy

```python
# docs/generator.py
# DOC_LINK: DOC-PAT-EXECUTION-LIBRARY-001

from pathlib import Path
from typing import List, Dict

def generate_module_docs(modules: List[Dict], template_path: Path, output_dir: Path):
    """Generate standardized docs for multiple modules."""
    template = template_path.read_text()
    
    for module in modules:
        doc_content = template
        for key, value in module.items():
            doc_content = doc_content.replace(f"{{{key}}}", value)
        
        output_file = output_dir / f"{module['module_name']}.md"
        output_file.write_text(doc_content)
        print(f"✓ Created {output_file.name}")

# Usage:
modules_to_document = [
    {
        'doc_id': 'DOC-CORE-ORCHESTRATOR-001',
        'module_name': 'orchestrator',
        'purpose': 'Coordinate workstream execution across tools',
        'language': 'python',
        'quickstart_command': 'from core.engine import Orchestrator\norch = Orchestrator()',
        # ... more variables
    },
    # ... 20 more modules
]

generate_module_docs(modules_to_document, Path('templates/module-doc.md'), Path('docs/modules/'))
```

---

## EXEC-005: Config Multiplexer

### Problem
Creating configuration files for multiple environments/modules.

### Template

```yaml
# CONFIG TEMPLATE: {config_type}
# Variables: {vars}

config_id: {config_id}
environment: {environment}
module: {module_name}

settings:
  enabled: {enabled}
  log_level: {log_level}
  timeout: {timeout_seconds}
  retry_attempts: {retry_attempts}
  
connections:
  database:
    host: {db_host}
    port: {db_port}
    name: {db_name}
  
  cache:
    type: {cache_type}
    ttl: {cache_ttl}

features:
  {feature_1}: {feature_1_enabled}
  {feature_2}: {feature_2_enabled}

thresholds:
  max_{resource_1}: {threshold_1}
  max_{resource_2}: {threshold_2}
```

### Batch Strategy

```bash
# 1. Discovery
# Create configs for: dev, staging, prod
# Notice: Same structure, different values per env

# 2. Template
# Extract invariant structure -> templates/env-config.yaml
# Define environment-specific variables

# 3. Batch generation
python scripts/generate_configs.py \
  --template templates/env-config.yaml \
  --environments dev,staging,prod \
  --output config/

# 4. Verify
# Ground truth: config validates against schema
python scripts/validate_configs.py config/*.yaml
```

---

## EXEC-006: API Endpoint Factory

### Problem
Creating CRUD endpoints for multiple resources.

### Template

```python
# CRUD ENDPOINT TEMPLATE
# Variables: {resource}, {schema}, {table}

from fastapi import APIRouter, HTTPException
from {schema_module} import {ResourceSchema}
from core.db import get_db

router = APIRouter(prefix="/api/{resource_plural}", tags=["{resource_plural}"])

@router.post("/")
async def create_{resource_singular}(data: {ResourceSchema}):
    """Create new {resource_singular}."""
    db = get_db()
    
    # Validate
    validated = {ResourceSchema}.validate(data)
    
    # Insert
    result = db.insert("{db_table}", validated.dict())
    
    return {"status": "success", "data": result}

@router.get("/{id}")
async def get_{resource_singular}(id: str):
    """Get {resource_singular} by ID."""
    db = get_db()
    
    result = db.query("{db_table}").filter(id=id).first()
    
    if not result:
        raise HTTPException(404, "{resource_singular} not found")
    
    return {"status": "success", "data": result}

@router.put("/{id}")
async def update_{resource_singular}(id: str, data: {ResourceSchema}):
    """Update {resource_singular}."""
    db = get_db()
    
    validated = {ResourceSchema}.validate(data)
    result = db.update("{db_table}", id, validated.dict())
    
    return {"status": "success", "data": result}

@router.delete("/{id}")
async def delete_{resource_singular}(id: str):
    """Delete {resource_singular}."""
    db = get_db()
    
    db.delete("{db_table}", id)
    
    return {"status": "success"}
```

### Execution

```markdown
**AI Prompt:**

Using the CRUD endpoint template in `templates/crud-endpoint.py`, 
create endpoints for the following resources:

1. users (User, users table)
2. projects (Project, projects table)
3. tasks (Task, tasks table)
4. comments (Comment, comments table)
5. attachments (Attachment, attachments table)

Batch create all 5 endpoint files.

Ground truth verification:
- All files created in api/endpoints/
- Server starts without errors
- Swagger docs show all endpoints
```

---

## EXEC-007: Schema Generator

### Problem
Creating JSON schemas for multiple data models.

### Template

```json
{
  "doc_id": "{doc_id}",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "{ResourceName} Schema",
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier"
    },
    "{field_1}": {
      "type": "{field_1_type}",
      "description": "{field_1_description}"
    },
    "{field_2}": {
      "type": "{field_2_type}",
      "description": "{field_2_description}"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": ["{required_fields}"],
  "additionalProperties": false
}
```

---

## Pattern Application Framework

### Decision Matrix

Use this to choose which pattern to apply:

| If you need to... | Use Pattern | Expected Savings |
|------------------|-------------|------------------|
| Create 10+ similar files | EXEC-001 | 58-62% |
| Generate code modules | EXEC-002 | 45-67% |
| Write test suites | EXEC-003 | 50-70% |
| Standardize documentation | EXEC-004 | 60-65% |
| Create configs | EXEC-005 | 70-75% |
| Build CRUD endpoints | EXEC-006 | 80-85% |
| Generate schemas | EXEC-007 | 55-60% |

### Application Checklist

Before starting work:

- [ ] **Pattern Recognition**: Is this repetitive? (2+ similar items)
- [ ] **Discovery Phase**: Create 2-3 examples manually
- [ ] **Pattern Selection**: Which EXEC pattern fits?
- [ ] **Template Creation**: Extract invariants (30 min)
- [ ] **Pre-decisions**: Answer all structural questions
- [ ] **Batch Grouping**: Group all similar items
- [ ] **Parallel Execution**: Can items be created in parallel?
- [ ] **Ground Truth**: Define "done" criterion
- [ ] **Verification Strategy**: Spot check only

### Execution Commands

```bash
# Pattern EXEC-001: Batch File Creator
python scripts/batch_file_creator.py \
  --template templates/module-manifest.yaml \
  --items-file items.json \
  --output-dir manifests/ \
  --batch-size 6

# Pattern EXEC-003: Test Suite Multiplier
python scripts/generate_tests.py \
  --template templates/test-suite.py \
  --functions validate_user,validate_project,validate_task \
  --output tests/

# Pattern EXEC-005: Config Multiplexer
python scripts/generate_configs.py \
  --template templates/env-config.yaml \
  --environments dev,staging,prod \
  --output config/

# Verification
python scripts/verify_pattern_output.py \
  --pattern EXEC-001 \
  --output-dir manifests/ \
  --expected-count 17
```

---

## Success Metrics

### Before Patterns

- Average time per item: 30-45 min
- Decision points per item: 12-15
- Context switches: 8-10
- Psychological friction: High
- Scalability: Linear (N × time)

### After Patterns

- Average time per item: 5-10 min
- Decision points per item: 2-3
- Context switches: 0-1
- Psychological friction: Minimal
- Scalability: Sublinear (overhead + N × small_time)

### ROI

```
Template creation: 2 hours (one-time)
Break-even point: 5 items
10 items: 56% time savings
20 items: 63% time savings
50 items: 75% time savings
```

---

## Next Steps

1. **Choose your pattern** based on current work
2. **Run discovery phase** (2-3 manual examples)
3. **Create template** (use patterns above as starting point)
4. **Batch execute** with AI assistance
5. **Measure results** and refine template

**The golden rule:**

> Decide once → Apply N times → Trust ground truth → Move on

---

**END OF EXECUTION PATTERNS LIBRARY**
