---
doc_id: DOC-GUIDE-TEMPLATE-STANDARDS-001
version: 1.0.0
created: 2025-12-09
last_updated: 2025-12-09
status: active
---

# Template Standardization Guidelines

**Purpose**: Establish consistent standards for all templates in the UET framework to ensure maintainability, discoverability, and ease of use.

---

## 1. File Naming Conventions

### Standard Format
```
{category}_{name}_{type}.{extension}
```

### Categories (Prefix)
- `doc_` - Documentation templates (READMEs, guides, reports)
- `code_` - Code/implementation templates (Python, YAML, JSON)
- `test_` - Test file templates
- `spec_` - Specification/contract templates
- `plan_` - Planning/design templates
- `config_` - Configuration templates

### Examples
```
✅ CORRECT:
doc_readme_module.md.template
code_api_endpoint.py.template
test_unit_standard.py.template
spec_module_api.md.template
plan_implementation.md.template
config_logging.json.template

❌ INCORRECT:
README_TEMPLATE.md
api_endpoint.py.template
test_case.py.template
TEMPLATE_MODULE_PUBLIC_API.md
```

### File Extension Rules
- **Always use double extensions**: `{name}.{target_ext}.template`
  - `*.md.template` → produces `.md` files
  - `*.py.template` → produces `.py` files
  - `*.yaml.template` → produces `.yaml` files
  - `*.json.template` → produces `.json` files
- **Exception**: Pure examples use actual extension (e.g., `example-items.json`)

---

## 2. Template Metadata (YAML Frontmatter)

### Required Fields (All Templates)
```yaml
---
doc_id: DOC-{CATEGORY}-{NAME}-{NNN}
version: {major}.{minor}.{patch}
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
status: active | deprecated | draft
template_type: code | documentation | specification | configuration | test
target_extension: .py | .md | .yaml | .json
---
```

### Optional Fields (Highly Recommended)
```yaml
category: module | api | workflow | phase | verification
purpose: "One-line description of what this template creates"
author: "Team/Person name"
based_on: "Reference to source document/pattern"
proven_uses: 0-N
estimated_time_minutes: N
supersedes: "Previous template ID (if applicable)"
related_templates:
  - "Related template ID 1"
  - "Related template ID 2"
```

### Full Example
```yaml
---
doc_id: DOC-CODE-API-ENDPOINT-001
version: 1.0.0
created: 2025-12-09
last_updated: 2025-12-09
status: active
template_type: code
target_extension: .py
category: api
purpose: "Create RESTful CRUD endpoint following UET patterns"
author: "UET Framework Team"
based_on: "UET Decision Elimination Playbook - CRUD pattern"
proven_uses: 0
estimated_time_minutes: 15
related_templates:
  - "DOC-TEST-API-ENDPOINT-001"
  - "DOC-SPEC-API-CONTRACT-001"
---
```

---

## 3. Variable Placeholder Standards

### Format Rules
Use **consistent placeholder syntax** based on context:

#### 3.1 Configuration/Structural Variables (ALL CAPS)
Use for high-level configuration that affects structure:
```python
PROJECT_ROOT = "${PROJECT_ROOT}"
MODULE_PATH = "${MODULE_PATH}"
LAYER = "${LAYER}"  # infra, domain, api, ui
STATUS = "${STATUS}"
```

#### 3.2 Code Identifiers (PascalCase or snake_case)
Use for code elements that follow language conventions:

**Python:**
```python
class ${ClassName}:
    def ${method_name}(self, ${param_name}: ${ParamType}) -> ${ReturnType}:
        pass
```

**JavaScript/TypeScript:**
```javascript
class ${ClassName} {
    ${methodName}(${paramName}: ${ParamType}): ${ReturnType} {
    }
}
```

#### 3.3 Documentation Placeholders (Descriptive)
Use clear, descriptive names in documentation:
```markdown
# ${module_name_human_readable}

**Purpose**: ${purpose_description}

## Key Features
- ${feature_1}
- ${feature_2}
```

### Variable Naming Conventions

| Context | Format | Example |
|---------|--------|---------|
| File paths | SCREAMING_SNAKE_CASE | `${MODULE_PATH}`, `${TEST_DIR}` |
| Class names | PascalCase | `${ClassName}`, `${ServiceName}` |
| Function/method names | snake_case | `${function_name}`, `${method_name}` |
| Variables | snake_case | `${variable_name}`, `${param_name}` |
| Constants | SCREAMING_SNAKE_CASE | `${MAX_RETRIES}`, `${DEFAULT_TIMEOUT}` |
| Type names | PascalCase | `${TypeName}`, `${SchemaName}` |
| Documentation sections | lowercase with spaces | `${purpose description}`, `${usage example}` |

### Required Variable Documentation
Every template MUST include a variables section:

```markdown
## Template Variables

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `MODULE_NAME` | string | Yes | - | Name of the module (snake_case) |
| `MODULE_PATH` | path | Yes | - | Relative path from project root |
| `LAYER` | enum | Yes | - | One of: infra, domain, api, ui |
| `AUTHOR` | string | No | "UET Team" | Module author name |
```

---

## 4. Template Structure Standards

### 4.1 Code Templates

```python
# {Template Name}
# 
# TEMPLATE METADATA
# doc_id: ${DOC_ID}
# version: ${VERSION}
# 
# TEMPLATE VARIABLES
# - ${variable_1}: ${description_1}
# - ${variable_2}: ${description_2}
#
# USAGE
# Fill in all ${VARIABLE} placeholders before use
# 
# Based on: ${source_pattern_or_guide}

from typing import ${required_types}

# Template implementation starts here
```

### 4.2 Documentation Templates

```markdown
---
# Frontmatter (see section 2)
---

# ${Title}

**Purpose**: ${one_line_purpose}

## Template Variables
[See table above]

## Instructions
1. ${step_1}
2. ${step_2}
3. ${step_3}

## Template Content Starts Here

[Actual template content with ${VARIABLES}]

---

## Usage Example

[Complete example showing filled-in template]

---

## Checklist
- [ ] All variables filled in
- [ ] No ${PLACEHOLDERS} remaining
- [ ] Tests passing (if applicable)
```

### 4.3 Configuration Templates

```yaml
# Configuration Template: ${config_name}
# 
# doc_id: ${DOC_ID}
# version: ${VERSION}
#
# VARIABLES:
# - ${var_1}: ${description}
# - ${var_2}: ${description}

# Configuration content
${config_key}: ${config_value}
```

---

## 5. Documentation Requirements

### Every Template MUST Include:

#### 5.1 Header Section
- Template name and purpose
- Version and status
- Author and creation date
- Source/inspiration (if applicable)

#### 5.2 Variables Section
- Complete list of all variables
- Type, required/optional, defaults
- Clear descriptions

#### 5.3 Instructions Section
- Step-by-step usage guide
- Prerequisites (if any)
- Expected outcomes

#### 5.4 Example Section
- At least one complete example
- Shows filled-in template
- Demonstrates expected output

#### 5.5 Validation Section
- Checklist for completion
- Quality criteria
- Testing requirements (if applicable)

---

## 6. Quality Standards

### 6.1 Completeness
- ✅ No placeholder code (TODO, FIXME, ...)
- ✅ All functions/methods fully implemented OR marked as "implementation detail"
- ✅ No placeholder comments without actual implementation
- ✅ All imports specified

### 6.2 Self-Documentation
- ✅ Clear variable names that explain purpose
- ✅ Comments only where logic is complex
- ✅ Docstrings for all public functions
- ✅ Type hints for all function signatures

### 6.3 Testability
- ✅ Code templates include corresponding test template reference
- ✅ Test templates follow same structure as code
- ✅ Minimum 3 test cases: happy path, error case 1, error case 2

### 6.4 Maintainability
- ✅ Version tracked in frontmatter
- ✅ Change log for versions > 1.0.0
- ✅ Deprecation notices if replaced
- ✅ Migration guide if breaking changes

---

## 7. Template Categories & Organization

### Directory Structure
```
templates/
├── code/                           # Code implementation templates
│   ├── python/
│   │   ├── code_api_endpoint.py.template
│   │   ├── code_module_class.py.template
│   │   └── code_cli_script.py.template
│   ├── yaml/
│   │   ├── code_workflow_spec.yaml.template
│   │   └── code_phase_plan.yaml.template
│   └── shell/
│       └── code_batch_script.ps1.template
│
├── test/                           # Test templates
│   ├── test_unit_standard.py.template
│   ├── test_integration.py.template
│   └── test_contract_validation.py.template
│
├── doc/                            # Documentation templates
│   ├── doc_readme_module.md.template
│   ├── doc_api_reference.md.template
│   ├── doc_implementation_plan.md.template
│   └── doc_decision_record.md.template
│
├── spec/                           # Specification templates
│   ├── spec_module_api.md.template
│   ├── spec_io_contract.md.template
│   └── spec_workstream.yaml.template
│
├── config/                         # Configuration templates
│   ├── config_logging.json.template
│   ├── config_git_workflow.yaml.template
│   └── config_ci_pipeline.yaml.template
│
├── plan/                           # Planning templates
│   ├── plan_implementation.md.template
│   ├── plan_phase_execution.md.template
│   └── plan_sprint.md.template
│
└── examples/                       # Example files (not templates)
    ├── example-items.json
    └── example-module-manifest.yaml
```

---

## 8. Template Lifecycle

### 8.1 Creation Process
1. **Identify pattern** - Find repeating work that can be templated
2. **Document pattern** - Write down decisions/structure
3. **Create template** - Follow naming/structure standards
4. **Add metadata** - Complete frontmatter
5. **Write documentation** - Variables, instructions, examples
6. **Test template** - Use it to create real artifact
7. **Review** - Ensure quality standards met
8. **Publish** - Commit with clear message

### 8.2 Versioning
- **Patch (1.0.X)**: Typos, clarifications, no structural changes
- **Minor (1.X.0)**: New optional variables, backwards compatible
- **Major (X.0.0)**: Breaking changes, structural modifications

### 8.3 Deprecation
When replacing a template:
```yaml
---
status: deprecated
superseded_by: "DOC-CODE-NEW-TEMPLATE-001"
deprecation_date: "2025-12-31"
removal_date: "2026-03-31"
migration_guide: "See docs/migrations/001-to-002.md"
---
```

---

## 9. Validation & Testing

### 9.1 Template Validation Checklist
Before committing a new template:

- [ ] **Naming**: Follows `{category}_{name}_{type}.{ext}.template` format
- [ ] **Frontmatter**: All required fields present and valid
- [ ] **Variables**: All documented in variables table
- [ ] **Instructions**: Clear step-by-step usage guide
- [ ] **Example**: At least one complete working example
- [ ] **Validation**: Checklist for template users included
- [ ] **Testing**: Template has been used to create real artifact
- [ ] **Quality**: No TODOs, FIXMEs, or placeholder code
- [ ] **Documentation**: Purpose, usage, and outcomes clear

### 9.2 Template Testing Process
1. Create new branch
2. Use template to generate real artifact
3. Verify generated artifact meets quality standards
4. Document any issues or improvements
5. Update template before committing

---

## 10. Migration Plan (Existing Templates)

### Phase 1: Inventory (Week 1)
- [ ] List all existing templates
- [ ] Categorize by type
- [ ] Identify duplicates/overlaps

### Phase 2: Rename (Week 2)
- [ ] Rename files to follow standards
- [ ] Update any references in code/docs
- [ ] Create mapping document (old → new names)

### Phase 3: Standardize Metadata (Week 3)
- [ ] Add frontmatter to all templates
- [ ] Assign doc_ids
- [ ] Set initial versions (1.0.0)
- [ ] Add creation dates (use git history if possible)

### Phase 4: Document Variables (Week 4)
- [ ] Standardize variable naming
- [ ] Create variables table for each template
- [ ] Add descriptions for all variables

### Phase 5: Add Examples (Week 5)
- [ ] Create working example for each template
- [ ] Test examples to ensure they work
- [ ] Document expected outcomes

### Phase 6: Reorganize (Week 6)
- [ ] Create new directory structure
- [ ] Move templates to appropriate folders
- [ ] Update index/registry
- [ ] Archive deprecated templates

---

## 11. Template Registry

### Master Registry File
Create `templates/TEMPLATE_REGISTRY.yaml`:

```yaml
registry:
  version: 1.0.0
  last_updated: "2025-12-09"
  
templates:
  - doc_id: "DOC-CODE-API-ENDPOINT-001"
    name: "code_api_endpoint.py.template"
    path: "templates/code/python/code_api_endpoint.py.template"
    category: "code"
    type: "api"
    status: "active"
    version: "1.0.0"
    purpose: "Create RESTful CRUD endpoint"
    proven_uses: 5
    
  - doc_id: "DOC-TEST-UNIT-STANDARD-001"
    name: "test_unit_standard.py.template"
    path: "templates/test/test_unit_standard.py.template"
    category: "test"
    type: "unit"
    status: "active"
    version: "1.0.0"
    purpose: "Standard unit test structure"
    proven_uses: 12
    
  # ... more templates
```

---

## 12. Best Practices

### DO ✅
- Use descriptive variable names
- Provide working examples
- Include validation checklists
- Version your templates
- Test before committing
- Document all assumptions
- Link to related templates
- Keep templates focused (single responsibility)

### DON'T ❌
- Mix multiple patterns in one template
- Leave placeholder code (TODO, FIXME)
- Use inconsistent variable naming
- Skip the documentation sections
- Create templates without testing them
- Hardcode values that should be variables
- Forget to update version on changes
- Create templates for one-time use

---

## 13. Quick Reference

### Creating a New Template

```bash
# 1. Choose name following convention
name="code_service_class.py.template"

# 2. Create file with frontmatter
cat > templates/code/python/$name << 'EOF'
---
doc_id: DOC-CODE-SERVICE-CLASS-001
version: 1.0.0
created: $(date +%Y-%m-%d)
last_updated: $(date +%Y-%m-%d)
status: draft
template_type: code
target_extension: .py
category: service
purpose: "Create service class with dependency injection"
---

# Template content here...
EOF

# 3. Add to registry
# Edit templates/TEMPLATE_REGISTRY.yaml

# 4. Test the template
# Use it to create real file

# 5. Update status to 'active'
# Commit with clear message
```

---

## 14. Support & Maintenance

### Template Maintainers
- **Owner**: UET Framework Team
- **Review Cycle**: Quarterly
- **Issue Tracking**: GitHub Issues with label `template`

### Getting Help
- For template usage questions: Check template's example section
- For template bugs: File issue with label `template-bug`
- For new template requests: File issue with label `template-request`
- For template improvements: Submit PR with label `template-enhancement`

---

## Appendix A: Template Naming Quick Reference

| Current Name | Standard Name | Category |
|--------------|---------------|----------|
| `README_TEMPLATE.md` | `doc_readme_module.md.template` | doc |
| `api_endpoint.py.template` | `code_api_endpoint.py.template` | code |
| `test_case.py.template` | `test_unit_standard.py.template` | test |
| `TEMPLATE_MODULE_PUBLIC_API.md` | `spec_module_api.md.template` | spec |
| `TEMPLATE_IMPLEMENTATION_PLAN.md` | `plan_implementation.md.template` | plan |
| `NEW_SHARED_MODULE_TEMPLATE.md` | `doc_module_creation_guide.md.template` | doc |
| `decision_record.md.template` | `doc_decision_record.md.template` | doc |
| `logging-config.json` | `config_logging.json.template` | config |
| `module_manifest.template` | `doc_module_manifest.md.template` | doc |
| `test_module_template.py` | `test_module_standard.py.template` | test |

---

## Appendix B: Variable Naming Examples

### Good Variable Names ✅
```python
${MODULE_NAME}              # Clear, specific
${service_type}             # Descriptive
${max_retry_attempts}       # Self-documenting
${UserAccountClass}         # Follows Python convention
${api_endpoint_path}        # Clear purpose
```

### Bad Variable Names ❌
```python
${name}                     # Too generic
${var1}                     # Non-descriptive
${X}                        # Single letter
${thing}                    # Vague
${data}                     # Ambiguous
```

---

**End of Template Standards**

**Document Status**: Active
**Version**: 1.0.0
**Last Updated**: 2025-12-09
**Next Review**: 2026-03-09
