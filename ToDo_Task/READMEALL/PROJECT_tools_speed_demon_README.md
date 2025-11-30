---
doc_id: DOC-GUIDE-PROJECT-TOOLS-SPEED-DEMON-README-1590
---

# Speed Demon Replication System

**Created**: 2025-11-23  
**Purpose**: Systematize 67% faster execution for all future work  
**Status**: Production-ready

---

## Quick Start

```bash
# 1. Start new phase
cd tools/speed_demon
python analyze_phase.py --phase "New documentation task"

# 2. After 3 examples, extract template
python extract_template.py --examples file1 file2 file3 --output templates/my.template

# 3. Batch create remaining items
python batch_create.py --template templates/my.template --spec batch.json

# 4. Verify ground truth
python verify_ground_truth.py --spec verify.json

# 5. Track metrics
python track_metrics.py --phase "PH-XX" --actual 6h --planned 15h
```

---

## Core Components

### 1. Templates (`templates/`)
- `module_manifest.template` - Module documentation
- `phase_plan.template` - Phase planning
- `session_summary.template` - Progress tracking

### 2. Scripts (`tools/speed_demon/`)
- `batch_create.py` - Parallel file generation
- `extract_template.py` - Auto-extract patterns
- `verify_ground_truth.py` - Observable evidence verification
- `track_metrics.py` - Speed tracking

### 3. Playbooks (`docs/playbooks/`)
- `speed_demon_execution.md` - Step-by-step guide
- `ai_agent_instructions.md` - AI-specific rules

### 4. Governance (`config/`)
- `speed_demon_policy.yaml` - Mandatory practices

---

## The 5 Speed Techniques

### 1. Parallel Creation
**When**: Operations are independent  
**How**: Batch tool calls in single LLM turn  
**Savings**: 42% time reduction

### 2. Template-Based
**When**: After 3+ similar items  
**How**: Extract pattern, apply ruthlessly  
**Savings**: 80% per-item reduction

### 3. Atomic Execution
**When**: Always  
**How**: 1 file = 1 operation, no cascading  
**Savings**: 60% coordination overhead

### 4. No Verification Overhead
**When**: Documentation or well-tested code  
**How**: Ground truth only (file exists, exit 0)  
**Savings**: 10 min/item

### 5. Ground Truth
**When**: Always  
**How**: Trust observable outputs  
**Savings**: Zero second-guessing

---

## Replication Checklist

For any new phase:

- [ ] Analyze if work is repetitive
- [ ] If yes (>3 similar items), plan for templates
- [ ] Execute first 3 examples manually
- [ ] Extract template after #3
- [ ] Batch remaining work (parallel)
- [ ] Verify with ground truth only
- [ ] Track metrics
- [ ] Update templates for future use

---

## Success Criteria

This system works if:

✅ Future phases are 50%+ faster  
✅ Templates created within first 20% of time  
✅ 60%+ of work is batched  
✅ Verification < 10% of total time  
✅ Patterns reused across projects

---

## Examples

See:
- `devdocs/sessions/ai-navigation-v2/` - Real execution example
- `devdocs/speed_demon_case_study.md` - Detailed analysis

---

**Next**: Create your first template or run `analyze_phase.py`
