---
doc_id: DOC-QUICK-SSOT-POLICY-001
role: quick_reference
---

# SSOT Policy Quick Reference Card

## 🎯 What It Does

**Enforces**: Every SSOT doc → must have glossary term  
**How**: Pre-commit + CI automation  
**Benefit**: Zero cognitive load

## ⚡ Quick Commands

```bash
# Validate policy
python scripts/glossary_ssot_policy.py

# See all SSOT docs
python scripts/glossary_ssot_policy.py --verbose
```

## 📝 Mark File as SSOT

**Add to front-matter**:
```yaml
---
doc_id: DOC-SPEC-NAME-001
ssot: true
ssot_scope: [domain]
---
```

## 📚 Add Glossary Term

**In `glossary/.glossary-metadata.yaml`**:
```yaml
terms:
  TERM-SPEC-NAME:
    name: "System Name"
    category: "Specifications"  # or Framework/Contract/GlobalService/CoreConcept
    implementation:
      files:
        - "path/to/spec.md"
```

## ✅ Valid Categories

- `Specifications`
- `Framework`
- `GlobalService`
- `Contract`
- `CoreConcept`

## 🔧 Common Fixes

### Missing glossary term
→ Add term with `implementation.files: ["path/to/doc.md"]`

### Missing doc_id
→ Add `doc_id: DOC-CAT-NAME-NNN` to front-matter

### File moved
→ Update `implementation.files` in glossary term

## 📖 Full Docs

- **Spec**: `glossary/specs/GLOSSARY_SSOT_POLICY_SPEC.md`
- **Guide**: `glossary/SSOT_POLICY_README.md`
- **Config**: `glossary/config/glossary_ssot_policy.yaml`
- **Validator**: `scripts/glossary_ssot_policy.py`

## 🚀 CI Setup

**Pre-commit**:
```yaml
- id: glossary-ssot-policy
  entry: python scripts/glossary_ssot_policy.py
  language: system
```

**GitHub Actions**:
```yaml
- run: python scripts/glossary_ssot_policy.py
```

---

**Remember**: You don't have to remember this. CI will catch it. 🎯
