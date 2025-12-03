---
doc_id: DOC-PAT-EXECUTION-PATTERNS-CHEATSHEET-748
---

# Execution Patterns - Quick Reference

**Speed Up Development: 3x-10x faster through decision elimination**

---

## 🚀 Quick Pattern Selector

| You need to... | Use | Command | Savings |
|---------------|-----|---------|---------|
| Create 10+ similar files | EXEC-001 | `batch_file_creator.py` | 58-62% |
| Find repetitive work | Discovery | `pattern_discovery.py` | N/A |
| Generate code modules | EXEC-002 | Prompt with template | 45-67% |
| Write test suites | EXEC-003 | Test template | 50-70% |
| Standardize docs | EXEC-004 | Doc template | 60-65% |
| Create configs | EXEC-005 | Config template | 70-75% |
| Build CRUD endpoints | EXEC-006 | API template | 80-85% |

---

## 📋 The 4-Phase Pattern

```
1. DISCOVERY (90 min)
   └─ Create 2-3 examples manually
   └─ Extract what's the same

2. TEMPLATE (30 min)
   └─ Create template file
   └─ Mark variables: {var}

3. BATCH (5 min/item)
   └─ Load template
   └─ Fill N times
   └─ Verify: files exist

4. TRUST (2 min)
   └─ Spot check 2 files
   └─ Move on
```

---

## ⚡ Common Commands

### Discover Patterns
```bash
# Find similar files automatically
python scripts/pattern_discovery.py --analyze core/ error/ aim/ --suggest

# Generate template starters
python scripts/pattern_discovery.py \
    --analyze docs/ \
    --pattern "*.md" \
    --suggest \
    --generate-templates templates/
```

### Batch Create Files
```bash
# From JSON
python scripts/batch_file_creator.py \
    --template templates/module-manifest.yaml \
    --items items.json \
    --output manifests/

# From CSV
python scripts/batch_file_creator.py \
    --template templates/config.yaml \
    --items items.csv \
    --output config/ \
    --batch-size 10
```

### Generate Items List
```json
[
  {
    "filename": "core.manifest.yaml",
    "variables": {
      "module": "core",
      "purpose": "Core engine",
      "layer": "domain"
    }
  },
  {
    "filename": "error.manifest.yaml",
    "variables": {
      "module": "error",
      "purpose": "Error detection",
      "layer": "domain"
    }
  }
]
```

---

## 🎯 Decision Elimination Checklist

Before starting work:

```markdown
PRE-DECISIONS (make once):
☐ Format: {Markdown|YAML|JSON|Python}
☐ Length: {50-100|100-200|200+} lines
☐ Detail level: {high-level|detailed|exhaustive}
☐ Verification: {file exists|runs|tests pass}
☐ When done: {N files created|all tests pass}

NOT DECISIONS (don't waste time):
☐ Perfect grammar: NO
☐ Exhaustive coverage: NO
☐ Optimal organization: NO
☐ Future-proof design: NO
```

---

## 📝 Template Format

```yaml
# TEMPLATE: {type}
# Variables: {var1}, {var2}, {var3}
# Time savings: {percentage}%

# STRUCTURAL DECISIONS (made once):
# - Format: {decision}
# - Length: {decision}
# - Detail level: {decision}

# VARIABLE SECTIONS (fill per instance):
{section_1}: {var1}
{section_2}: {var2}

# INVARIANTS (never change):
- {constant_1}
- {constant_2}

# EXAMPLE (filled template):
{working_example}
```

---

## 🔄 Execution Flow

```
┌─────────────────┐
│  Have 2-3       │
│  similar items? │
└────────┬────────┘
         │ YES
         ▼
┌─────────────────┐
│  Extract        │
│  pattern        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Create         │
│  template       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Batch create   │
│  N items        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ground truth   │
│  verify only    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DONE           │
│  Move on        │
└─────────────────┘
```

---

## 💡 Key Principles

1. **Decide Once, Apply N Times**
   - Make structural decisions in template
   - No per-item decisions during batch

2. **Trust Ground Truth**
   - File exists = success
   - Not "file is perfect"

3. **Batch by Similarity**
   - Group same-template items
   - Minimize context switching

4. **Parallel When Possible**
   - Create 4-6 files at once
   - Verify all at end

5. **Skip Perfectionism**
   - Content errors cheap to fix
   - Get files created first

---

## 📊 ROI Calculator

```
Template creation cost: 2 hours
Break-even: 5 items
Time per item: 5 min (vs 30 min manual)

10 items:  56% savings (2.5 hours saved)
20 items:  63% savings (5.3 hours saved)
50 items:  75% savings (16.7 hours saved)
```

---

## 🚫 Anti-Patterns to Avoid

❌ **Create template before 3 examples**  
✅ Do 3 naturally, then extract pattern

❌ **Template with 15 variables**  
✅ Template with ≤5 variables

❌ **Verify every detail per file**  
✅ Ground truth + spot check only

❌ **Do one at a time**  
✅ Batch create 4-6 at once

❌ **Abandon template on edge case**  
✅ Evolve template, don't abandon

---

## 🎓 Examples

### EXEC-001: Batch File Creator

```bash
# Create 17 module manifests
python scripts/batch_file_creator.py \
    --template templates/module-manifest.yaml \
    --items manifests.json \
    --output manifests/ \
    --batch-size 6

# Result: 5 min each vs 30 min each = 7 hours saved
```

### EXEC-004: Doc Standardizer

```markdown
# Prompt to AI:
Using the template in templates/module-doc.md, create documentation for:
- core/engine/orchestrator.py
- core/engine/scheduler.py
- core/engine/executor.py

Batch create all 3 docs. Ground truth: files exist with all sections.
```

### EXEC-006: API Endpoint Factory

```markdown
# Prompt to AI:
Using templates/crud-endpoint.py, create CRUD endpoints for:
- users (User, users table)
- projects (Project, projects table)
- tasks (Task, tasks table)

Batch create all 3 endpoint files.
Verify: Server starts, Swagger shows all endpoints.
```

---

## 📚 Full Documentation

- **Complete Guide**: `EXECUTION_PATTERNS_LIBRARY.md`
- **Decision Playbook**: `UTE_decision-elimination-playbook.md`
- **Pattern Scripts**: `scripts/batch_file_creator.py`, `scripts/pattern_discovery.py`

---

## 🏁 Quick Start

```bash
# 1. Find patterns in your codebase
python scripts/pattern_discovery.py --analyze . --suggest

# 2. Create template (30 min)
# Copy suggested template, fill in examples

# 3. Create items list
# items.json with filename + variables

# 4. Batch create
python scripts/batch_file_creator.py \
    --template templates/your-template.txt \
    --items items.json \
    --output output/

# 5. Verify and move on
ls output/ | wc -l  # Count matches expected
```

---

**The Golden Rule:**

> Decide once → Apply N times → Trust ground truth → Move on

---

**Time to value: 2 hours → 50+ hours saved over project lifetime**
