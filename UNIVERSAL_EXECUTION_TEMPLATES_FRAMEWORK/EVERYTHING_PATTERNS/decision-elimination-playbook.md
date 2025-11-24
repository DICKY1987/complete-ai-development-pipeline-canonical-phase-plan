# Decision Elimination Playbook
## Replicating Pattern Recognition Speed Across Any Execution Context

---

## Core Principle

**Speed = Pre-made Decisions × Ruthless Pattern Application**

The manifest creation achieved 3x speedup not through better tools, but by:
1. Recognizing the pattern after 3 examples
2. Codifying it into a reusable template
3. Eliminating 85% of decision points on subsequent work

This works for ANY repetitive AI-assisted task.

---

## The Universal Pattern

### Phase 1: Discovery (First 2-3 Examples)
**Goal: Find what decisions you're actually making**

```
Example: Creating API endpoints
├─ First endpoint: 45 minutes (everything is a decision)
│  ├─ "What HTTP method?"
│  ├─ "How to structure response?"
│  ├─ "What error handling?"
│  ├─ "Where to validate?"
│  └─ "How to document?"
├─ Second endpoint: 30 minutes (some patterns emerge)
│  ├─ "Oh, all POST for mutations"
│  └─ "Always JSON response with status/data/error"
└─ Third endpoint: 20 minutes (pattern solidifying)
   └─ "This is basically fill-in-the-blanks now"
```

**Action Items:**
- [ ] Do first example slowly, document EVERY decision you make
- [ ] Do second example, note which decisions repeated
- [ ] Do third example, extract the invariants

### Phase 2: Template Creation (30 minutes)
**Goal: Convert pattern to executable artifact**

**Template Types by Context:**

| Context | Template Format | Example |
|---------|----------------|---------|
| File creation | Literal file with placeholders | `.ai-module-manifest` with `<MODULE>` markers |
| Code generation | Function skeleton | `def api_endpoint_{name}(request): ...` |
| Documentation | Markdown outline | `## {Title}\n### Problem\n### Solution` |
| Configuration | YAML/JSON schema | `{name, purpose, entry_points, ...}` |
| Workflow steps | Checklist | `1. Create X, 2. Validate Y, 3. Deploy Z` |

**Template Quality Checklist:**
- [ ] Contains ALL structural decisions (no ad-hoc choices needed)
- [ ] Has clear placeholder syntax (`<THING>`, `{thing}`, `$THING`)
- [ ] Includes 1-2 filled examples as reference
- [ ] Fits on one screen (cognitive load constraint)
- [ ] Can be explained in 2 minutes

**Example Template Structure:**
```markdown
# Template: {TYPE}
# Purpose: One-line description of what this creates

## Structural Decisions (made once):
- Format: {JSON|YAML|Markdown}
- Length: {50-100|100-200|200+} lines
- Sections: {list}
- Detail level: {high-level|detailed|exhaustive}

## Variable Sections (fill per instance):
{section_1}: <describe what goes here>
{section_2}: <describe what goes here>

## Invariants (never change):
- {thing that's always the same}
- {another constant element}

## Example (filled template):
{complete working example}
```

### Phase 3: Batch Execution (scale without thinking)
**Goal: Apply template N times with minimal cognitive load**

**Batching Strategy:**

```python
# Pseudo-code for batch execution mindset
for item in items_to_create:
    context = load_item_specific_details(item)
    content = fill_template(template, context)
    create_tool_call(content)
    # NO verification, NO second-guessing
```

**Decision Elimination Checklist:**
- [ ] Group similar items together (same template applies)
- [ ] Load ALL context upfront (no mid-batch lookups)
- [ ] Trust template structure (no "should I adjust this?" questions)
- [ ] Use parallel execution where possible (batch tool calls)
- [ ] Skip perfectionism (file created = success)

**Cognitive Load Management:**
```
High cognitive load (AVOID):
  Think → Write → Verify → Think → Write → Verify (6 steps × N items)

Low cognitive load (REPLICATE):
  Load Template → Think Once → Write N × Batch Verify (3 steps total)
```

### Phase 4: Trust Ground Truth (stop overthinking)
**Goal: Define "done" objectively**

**Ground Truth Verification:**

| Context | Ground Truth | NOT Ground Truth |
|---------|-------------|------------------|
| File creation | File exists at path | Content is perfect |
| API deployment | Returns 200 OK | Code is elegant |
| Documentation | File committed to repo | Grammar is flawless |
| Test writing | Test runs and passes | 100% coverage |
| Config generation | Service starts successfully | All options specified |

**The Rule:** If ground truth passes, STOP WORKING. Refinement is future work.

---

## Replication Recipes

### Recipe 1: Creating Multiple Similar Files

**Context:** You need to create N files of similar type (configs, specs, docs, tests)

**Steps:**
1. **Discovery (30-90 min)**
   - Create first 2-3 files manually
   - After each, write down: "What did I decide that was the same?"
   - Extract decision list

2. **Template (30 min)**
   - Create `.template` file with placeholder syntax
   - Document: "For each new file, only these 3 things change"
   - Add one filled example

3. **Batch (5-10 min per file)**
   - List all target files: `aim, pm, scripts, tests, schema, config, ...`
   - For each: Load context → Fill template → Create file
   - Batch tool calls if possible (6 at once worked for manifests)

4. **Verify (2 min total)**
   - `ls -la target_dir/` - count files
   - Open 2 random files - spot check structure
   - Done

**Time Savings:**
- Without template: 30 min × 17 files = 8.5 hours
- With template: (90 min + 30 min + 5 min × 17) = 3.6 hours
- **Savings: 58% faster** (and scales better with N)

### Recipe 2: Repetitive Code Generation

**Context:** Adding similar functions, classes, or API endpoints

**Steps:**
1. **Discovery**
   ```python
   # First endpoint - discover pattern
   @app.post("/api/users")
   def create_user(request):
       validate(request, UserSchema)
       result = db.insert("users", request.data)
       return {"status": "ok", "data": result}
   
   # Second endpoint - pattern emerges
   @app.post("/api/projects")  # <- only this changes
   def create_project(request):  # <- and this
       validate(request, ProjectSchema)  # <- and this
       result = db.insert("projects", request.data)  # <- and this
       return {"status": "ok", "data": result}
   
   # Observation: 4 variables, 90% identical structure
   ```

2. **Template**
   ```python
   # FILE: templates/crud_endpoint.py
   @app.post("/api/{resource_plural}")
   def create_{resource_singular}(request):
       validate(request, {ResourceSchema})
       result = db.insert("{resource_table}", request.data)
       return {"status": "ok", "data": result}
   
   # USAGE INSTRUCTIONS:
   # Variables: resource_plural, resource_singular, ResourceSchema, resource_table
   # Example: users, user, UserSchema, users
   ```

3. **Batch**
   ```markdown
   Resources to create: users, projects, tasks, comments, attachments
   
   For each resource:
   - Write prompt: "Create CRUD endpoint for {resource} using crud_endpoint.py template"
   - Single LLM call with template context
   - Generate all 5 endpoints in one batch
   ```

4. **Verify**
   ```bash
   # Ground truth: endpoints respond
   curl -X POST localhost:8000/api/users -d '{"name":"test"}'
   curl -X POST localhost:8000/api/projects -d '{"name":"test"}'
   # Both return 200? Done.
   ```

### Recipe 3: Documentation Standardization

**Context:** Writing similar docs (API docs, module READMEs, runbooks)

**Steps:**
1. **Discovery**
   - Write 2-3 docs naturally
   - Notice: Same H2 sections keep appearing
   - Notice: Same level of detail each time

2. **Template**
   ```markdown
   # {Module Name}
   
   ## Purpose
   One sentence: {what it does}
   
   ## Quick Start
   ```bash
   {the one command to get started}
   ```
   
   ## Key Concepts
   - {concept_1}: {one-line explanation}
   - {concept_2}: {one-line explanation}
   (2-4 concepts, no more)
   
   ## Common Tasks
   ### {task_1}
   ```{language}
   {code example}
   ```
   
   ## Gotchas
   - {gotcha_1}
   - {gotcha_2}
   (real gotchas only, 2-4 items)
   
   ## Status
   - Maturity: {alpha|beta|stable}
   - Owner: {@person}
   ```

3. **Batch**
   - Modules: engine, validator, generator, indexer, ...
   - One prompt: "Using template, create docs for: {list}"
   - Parallel LLM calls with template context

4. **Verify**
   - `find docs/ -name README.md | wc -l` = expected count
   - Spot check 2 files for structure
   - Done (content errors fixed later)

### Recipe 4: Test Case Generation

**Context:** Writing similar test cases for different functions

**Steps:**
1. **Discovery**
   ```python
   # First test
   def test_validate_user():
       valid_input = {"name": "John", "email": "j@example.com"}
       result = validate_user(valid_input)
       assert result.success == True
       
       invalid_input = {"name": "John"}  # missing email
       result = validate_user(invalid_input)
       assert result.success == False
       assert "email" in result.errors
   
   # Pattern: happy path + 2-3 error cases
   ```

2. **Template**
   ```python
   # TEST TEMPLATE
   def test_{function_name}():
       # Happy path
       valid_input = {valid_example}
       result = {function_name}(valid_input)
       assert result.success == True
       
       # Error case 1: {error_type_1}
       invalid_input_1 = {invalid_example_1}
       result = {function_name}(invalid_input_1)
       assert result.success == False
       assert {expected_error_1} in result.errors
       
       # Error case 2: {error_type_2}
       ...
   ```

3. **Batch**
   - Functions: validate_user, validate_project, validate_task, ...
   - Prompt: "Generate tests for: {list} using template"
   - All tests in single tool call

4. **Verify**
   ```bash
   pytest tests/ -v
   # All pass? Done. Failures? Fix and move on.
   ```

---

## Decision Elimination Strategies

### Strategy 1: Pre-answer Questions

**Before starting work, document answers to:**

| Question | Pre-answered | Why |
|----------|-------------|-----|
| "How detailed?" | 50-100 lines, 2-4 examples | Eliminates scope creep |
| "What format?" | Markdown with YAML frontmatter | No format debates |
| "How verified?" | File exists + spot check 2 | No perfectionism |
| "When done?" | N files created | Clear exit criteria |
| "What if wrong?" | Fix later, content errors cheap | No decision paralysis |

**Make a `DECISIONS.md` at start:**
```markdown
# Pre-made Decisions for {Task}

## Structural Decisions (made once)
- Format: {decision}
- Length: {decision}
- Detail level: {decision}
- Verification: {decision}

## NOT Decisions (don't waste time on these)
- Perfect grammar: No
- Exhaustive coverage: No
- Optimal organization: No
- Future-proof design: No

## Ground Truth
Success = {specific observable criterion}
```

### Strategy 2: Batch by Similarity

**Group work by template, not by priority:**

```
❌ Poor Batching (by priority):
├─ P0: Create user API endpoint
├─ P0: Write deployment runbook
├─ P0: Add error logging
├─ P1: Create project API endpoint
└─ P1: Update deployment docs

✅ Good Batching (by template):
Batch 1: API Endpoints (same template)
├─ Create user endpoint
└─ Create project endpoint

Batch 2: Documentation (same template)
├─ Write deployment runbook
└─ Update deployment docs

Batch 3: Infrastructure (different template)
└─ Add error logging
```

**Benefits:**
- Load template context once
- No context switching
- Can batch tool calls
- Decision-free execution

### Strategy 3: Template Library

**Build reusable templates over time:**

```
templates/
├── README.md                    # Template index
├── api-endpoint.py              # CRUD endpoint template
├── test-suite.py                # Test case template
├── module-manifest.yaml         # Module documentation
├── deployment-runbook.md        # Operations documentation
├── config-schema.json           # Configuration template
└── workflow-phase.yaml          # Project phase plan
```

**Template Metadata:**
```yaml
# At top of each template file
# TEMPLATE: API Endpoint
# USE_CASE: Creating new CRUD endpoints
# TIME_SAVINGS: 30min -> 5min per endpoint
# VARIABLES: {resource_name, schema, validation_rules}
# LAST_USED: 2024-11-15
# SUCCESS_RATE: 23/25 endpoints (92%)
```

**Template Evolution:**
- After 5 uses: Optimize for most common variations
- After 10 uses: Extract sub-templates for complex sections
- After 20 uses: Automate with code generation

### Strategy 4: Parallel Execution

**Identify parallelizable work:**

```python
# Can parallelize when:
parallelizable = (
    operations_are_independent and
    no_shared_state_conflicts and
    ground_truth_is_observable
)

# Examples of parallelizable work:
- Creating multiple files in different directories
- Generating multiple similar code modules
- Writing multiple independent test cases
- Processing multiple data files
- Creating multiple API endpoints
```

**Implementation:**

For AI assistants (GitHub Copilot, Claude Code):
```xml
<!-- Single LLM turn with multiple tool calls -->
<create file="module_a.py">{content_a}</create>
<create file="module_b.py">{content_b}</create>
<create file="module_c.py">{content_c}</create>
<!-- Tool infrastructure processes in parallel -->
```

For scripts:
```python
from concurrent.futures import ThreadPoolExecutor

def create_from_template(item):
    content = template.fill(item)
    filesystem.create(item.path, content)

with ThreadPoolExecutor(max_workers=6) as executor:
    executor.map(create_from_template, items)
```

**Parallelism Checklist:**
- [ ] Operations are independent (no sequential dependencies)
- [ ] No file/resource conflicts (different paths)
- [ ] Success is observable (file exists, test passes)
- [ ] Failure handling is atomic (one fails ≠ all fail)

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Premature Template Creation
**Problem:** Creating template before understanding pattern

❌ Bad:
```
Day 1: Create template (guessing structure)
Day 2: First real file doesn't fit template
Day 3: Second file also doesn't fit
Day 4: Abandon template, start over
```

✅ Good:
```
Day 1: Create first 2-3 examples naturally
Day 2: Extract pattern from examples
Day 3: Create template from proven pattern
Day 4: Apply template to remaining 15 items
```

**Rule:** Need 3 examples before templating

### Anti-Pattern 2: Over-Engineering Templates
**Problem:** Making template too flexible/complex

❌ Bad Template (too many options):
```python
# Template with 15 configuration options
def {function_name}(
    {param1},
    {param2},
    {param3}={default3},
    {param4}={default4},
    enable_{feature1}=True,
    enable_{feature2}=False,
    mode={mode_option},
    ...
):
    # 200 lines of conditional logic
```

✅ Good Template (focused):
```python
# Template with 3 variables
def {function_name}({param1}, {param2}):
    validate({param1}, {Schema})
    result = process({param2})
    return {"status": "ok", "data": result}
```

**Rule:** Template should have ≤5 variables

### Anti-Pattern 3: Verification Perfectionism
**Problem:** Checking every detail before moving on

❌ Bad Verification:
```markdown
For each file created:
✓ File exists
✓ Syntax is valid
✓ All sections present
✓ No typos
✓ Follows style guide
✓ Cross-references work
✓ Examples are correct
✓ Documentation complete
(30 minutes per file)
```

✅ Good Verification:
```markdown
For all files:
✓ Count matches expected (17 files)
✓ Spot check 2 random files for structure
✓ Run automated validation (if exists)
(2 minutes total)
```

**Rule:** Ground truth + spot check only

### Anti-Pattern 4: Sequential When Parallel Works
**Problem:** Doing one at a time from habit

❌ Bad Execution:
```
Create file 1 → Wait → Verify → Think
Create file 2 → Wait → Verify → Think
Create file 3 → Wait → Verify → Think
(15 min × 17 files = 4.25 hours)
```

✅ Good Execution:
```
Load template → Think once
Batch create 6 files → Single wait
Batch create 6 files → Single wait
Batch create 5 files → Single wait
Verify all 17 → Done
(2 hours total)
```

**Rule:** If independent, do in parallel

### Anti-Pattern 5: Template Abandonment
**Problem:** Reverting to manual when edge case appears

❌ Bad Response to Edge Case:
```
Files 1-10: Use template (smooth)
File 11: Doesn't quite fit template
Decision: "Template doesn't work, go manual"
Files 12-17: Back to 30 min per file
```

✅ Good Response to Edge Case:
```
Files 1-10: Use template (smooth)
File 11: Doesn't quite fit template
Decision: "Add optional section to template"
Files 12-17: Continue with enhanced template
```

**Rule:** Evolve template, don't abandon

---

## Orchestration Integration

### For AI Boss Programs

**Template as Capability Metadata:**

```yaml
# capabilities/create-module-manifest.yaml
capability_id: create-module-manifest
category: documentation
template_file: templates/module-manifest.yaml

decision_template:
  structural:
    format: "YAML with specific sections"
    length: "50-100 lines"
    detail_level: "high-level overview, not exhaustive"
  
  ground_truth:
    success_criterion: "file_exists(path)"
    verification: "spot_check_structure"
    error_handling: "content_errors_fixed_later"
  
  variables:
    required: [module_name, purpose, layer]
    optional: [entry_points, key_patterns, gotchas]
    defaults:
      maturity: "alpha"
      test_coverage: "unknown"

execution_model:
  parallelism: true
  max_batch_size: 6
  dependencies: []
  estimated_time: "5 minutes per instance"

template_quality:
  proven_uses: 17
  success_rate: 1.0
  average_time: 5
  time_savings_vs_manual: 0.83
```

**Boss Program Decision Logic:**

```python
def execute_repetitive_task(task):
    # Check if template exists
    if has_template(task.type):
        template = load_template(task.type)
        
        # Batch similar items
        items = group_by_template(task.items)
        
        # Load ALL context upfront
        context = preload_context(items)
        
        # Execute in parallel batches
        for batch in chunk(items, template.max_batch_size):
            results = parallel_create([
                template.fill(item, context)
                for item in batch
            ])
            
            # Ground truth verification only
            assert all(ground_truth(r) for r in results)
        
        return "complete"
    else:
        # Discovery mode: learn pattern
        return learn_and_create_template(task)
```

### For Aider/Claude Code CLI Integration

**Template Files as Context:**

```bash
# Provide template to AI coding assistant
aider \
  --read templates/api-endpoint.py \
  --message "Create CRUD endpoints for: users, projects, tasks" \
  --batch-mode

# AI loads template, applies 3 times, batch creates
```

**Decision File as Instructions:**

```bash
# Provide decisions upfront
aider \
  --read DECISIONS.md \
  --read templates/module-manifest.yaml \
  --message "Create manifests for all modules in src/"
  
# DECISIONS.md contains:
# - Format: YAML
# - Length: 50-100 lines
# - Verification: file exists only
# - No perfectionism: content errors fixed later
```

---

## Success Metrics

### Before Template Application
```
Average time per item: 30-45 minutes
Decision points per item: 12-15
Context switches: 8-10
Verification time: 5-10 minutes
Psychological friction: High
```

### After Template Application
```
Average time per item: 5-10 minutes
Decision points per item: 2-3
Context switches: 0-1
Verification time: 30 seconds (spot check)
Psychological friction: Minimal
```

### ROI Calculation
```
Template Creation Cost:
  Discovery: 90 minutes (first 3 examples)
  Template: 30 minutes (write template)
  Total: 120 minutes (2 hours)

Break-Even Point:
  Time saved per item: 25 minutes
  Break-even at: 120 / 25 = 4.8 items
  ROI positive after: 5th item

Scale Benefits:
  10 items: 2.2 hours (vs 5 hours manual) = 56% savings
  20 items: 3.7 hours (vs 10 hours manual) = 63% savings
  50 items: 6.2 hours (vs 25 hours manual) = 75% savings
```

---

## Quick Start Checklist

**When facing repetitive work:**

- [ ] **Recognize the pattern** (after 2-3 examples)
- [ ] **Extract decisions made** (what was the same?)
- [ ] **Create template** (30 min investment)
- [ ] **Pre-answer questions** (format, length, verification)
- [ ] **Batch similar items** (group by template)
- [ ] **Load context upfront** (no mid-batch lookups)
- [ ] **Execute in parallel** (if independent)
- [ ] **Trust ground truth** (file exists = success)
- [ ] **Skip perfectionism** (content errors cheap to fix)
- [ ] **Measure and iterate** (refine template if needed)

**The golden rule:**

> Decide once → Apply N times → Trust ground truth → Move on

---

## Conclusion

Speed doesn't come from better tools or typing faster. Speed comes from **eliminating decisions through pattern recognition**.

The manifest creation achieved 3x speedup because:
1. Recognized pattern after 3 examples
2. Codified into reusable template
3. Applied ruthlessly to remaining 14 items
4. Eliminated 85% of decision overhead

This works for ANY repetitive task. The technique is universal.

**Next time you face repetitive work:**
1. Do 2-3 examples naturally
2. Notice what decisions repeat
3. Create template with those decisions baked in
4. Batch execute with zero thinking

That's the entire playbook.
