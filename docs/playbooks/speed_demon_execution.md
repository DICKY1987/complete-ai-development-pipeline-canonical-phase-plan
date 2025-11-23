# Speed Demon Execution Playbook

**Purpose**: Step-by-step guide to achieve 50-70% faster execution

---

## Phase 1: Pattern Recognition (First 10-20% of work)

**Goal**: Identify the repeatable pattern

**Steps**:
1. Execute first 2-3 examples manually
2. Document similarities vs differences
3. Extract common structure
4. Validate on example #4

**Time Budget**: 20% of total estimated time

**Outputs**:
- [ ] Template file exists
- [ ] Example #4 generated from template matches manual quality

**Ground Truth**:
```bash
# Template file created
ls templates/my_template.template

# Example #4 validates
diff manual_example4.txt generated_example4.txt
# Should be >90% identical
```

---

## Phase 2: Template Refinement (Next 10% of work)

**Goal**: Perfect the template for production use

**Steps**:
1. Apply template to examples #5-7
2. Note gaps, awkward sections, missing variables
3. Refine template structure
4. Re-generate examples #5-7, compare quality

**Time Budget**: 10% of total time

**Outputs**:
- [ ] Template generates 90%+ of content automatically
- [ ] Only domain-specific details need manual input

**Ground Truth**:
```bash
# Template quality check
python tools/speed_demon/template_quality.py \
  --template templates/my.template \
  --examples example5.txt example6.txt example7.txt
# Should report >90% coverage
```

---

## Phase 3: Batch Production (Remaining 60-70% of work)

**Goal**: Scale ruthlessly with parallelism

**Steps**:

1. **Identify all remaining items**
   ```bash
   # Example: 11 modules left to document
   ls -d */ | wc -l  # 11 directories
   ```

2. **Group by similarity** (batches of 4-6)
   ```
   Batch 1: Simple modules (tests, schema, config)
   Batch 2: Medium modules (scripts, infra)
   Batch 3: Complex modules (engine, gui)
   ```

3. **For each batch**:
   
   a. Create batch spec JSON:
   ```json
   {
     "specs": [
       {
         "output": "tests/.ai-module-manifest",
         "variables": {
           "MODULE_NAME": "tests",
           "ONE_LINE_PURPOSE": "Test suite: unit tests, integration tests",
           ...
         }
       },
       ...
     ]
   }
   ```
   
   b. Run batch creation:
   ```bash
   python tools/speed_demon/batch_create.py \
     --template templates/module_manifest.template \
     --spec batch_1.json
   ```
   
   c. Ground truth verify:
   ```bash
   python tools/speed_demon/verify_ground_truth.py \
     --spec verify_batch_1.json
   ```
   
   d. Move to next batch

**Time Budget**: 60% of total time

**Outputs**:
- [ ] All N items created
- [ ] Ground truth verification passes
- [ ] Zero manual verification needed

---

## Phase 4: Finalization (Final 10%)

**Goal**: Wrap up and document

**Steps**:
1. Run final comprehensive ground truth check
2. Create session summary
3. Update progress tracking
4. Commit results

**Time Budget**: 10% of total time

**Outputs**:
- [ ] Final verification passes
- [ ] Session summary exists
- [ ] Metrics tracked

**Ground Truth**:
```bash
# All items exist
python tools/speed_demon/verify_ground_truth.py --spec final_verify.json
# Exit code: 0

# Session summary created
ls devdocs/sessions/my-phase/SESSION_*.md
```

---

## Decision Trees

### Should I use a template?

```
Have I created 3+ similar items?
├─ YES → Extract template, use for remaining
└─ NO  → Continue manual (reevaluate after each item)
```

### Should I batch these operations?

```
Are all operations independent (no dependencies)?
├─ YES → Can they be done simultaneously?
│        ├─ YES → Batch them (parallel creation)
│        └─ NO  → Sequential execution
└─ NO  → Sequential execution (respect dependencies)
```

### How much detail in template?

```
Is this for AI consumption or human consumption?
├─ AI  → Medium detail (50-100 lines)
└─ Human → High detail (100-200 lines, with examples)
```

### Should I verify this worked?

```
What type of work?
├─ Documentation → File exists = success
├─ Code → Tests pass = success
└─ Infrastructure → Integration tests pass = success
```

---

## Anti-Patterns to Avoid

❌ **"Let me think about the perfect structure for 30 minutes"**  
✅ Copy proven pattern, adapt minimally (5 minutes)

❌ **"Let me manually create each of these 10 similar files"**  
✅ Create 3 manually, extract template, batch the rest

❌ **"Let me read each file back to verify it's correct"**  
✅ Trust the tool output (file created = success)

❌ **"Let me cross-reference all dependencies before starting"**  
✅ Living documentation, users will fix errors

❌ **"Let me make this 100% perfect before moving on"**  
✅ Good enough (90%) ships, perfect (100%) never finishes

---

## Example Execution Timeline

**Baseline** (without speed demon): 28-36 hours

**With speed demon**: 10-12 hours

```
Hour 0-2: Pattern recognition (3 examples manually)
Hour 2-3: Template extraction and refinement
Hour 3-5: Batch 1 creation (6 items in parallel)
Hour 5-7: Batch 2 creation (6 items in parallel)
Hour 7-9: Batch 3 creation (remaining items)
Hour 9-10: Ground truth verification
Hour 10-11: Finalization and documentation
Hour 11-12: Buffer (contingency)

Total: 12 hours (vs 28-36 baseline = 67% faster)
```

---

## Success Criteria

This playbook succeeds if:

✅ Phase completes 50%+ faster than baseline  
✅ Template created within first 20% of time  
✅ 60%+ of work done in batches  
✅ Verification < 10% of total time  
✅ Quality matches or exceeds manual approach  
✅ Pattern documented for future reuse

---

## Next Steps

After completing a phase with this playbook:

1. Update metrics in `tools/speed_demon/metrics/`
2. Refine templates based on learnings
3. Share patterns with team
4. Apply to next phase

**Continuous improvement**: Each phase should be faster than the last.
