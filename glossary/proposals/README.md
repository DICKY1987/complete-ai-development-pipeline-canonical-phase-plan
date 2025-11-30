---
doc_id: DOC-GUIDE-README-1406
---

# Glossary Term Proposals

**Purpose**: Store proposals for new glossary terms

---

## Overview

This directory contains proposals for new glossary terms awaiting architecture team review.

---

## Proposal Format

```yaml
# proposals/new-circuit-breaker-term.yaml

name: "Circuit Breaker"
category: "Core Engine"
proposed_by: "developer-name"
proposed_date: "2025-11-25"
status: "proposed"

definition: |
  Resilience pattern that prevents cascading failures by "opening" 
  (stopping) execution when error thresholds are exceeded.

rationale: |
  This concept appears frequently in core/engine/circuit_breakers.py 
  but lacks a glossary entry. It's referenced in multiple documents 
  and would benefit from a canonical definition.

implementation:
  files:
    - "core/engine/circuit_breakers.py"
  entry_points:
    - "CircuitBreaker.__init__()"
    - "CircuitBreaker.call()"

schema_refs:
  - "config/circuit_breaker.yaml"

related_terms:
  - term_id: TERM-ENGINE-001
    relationship: uses
  - term_id: TERM-ENGINE-002
    relationship: protects

usage_examples:
  - language: python
    code: |
      from core.engine.circuit_breakers import CircuitBreaker
      cb = CircuitBreaker(max_failures=3, timeout=300)
      result = cb.call(risky_operation)
    description: "Basic circuit breaker usage"

evidence:
  - "Referenced in 12 source files"
  - "Mentioned in DOC_ARCHITECTURE.md"
  - "Part of UET framework alignment"
```

---

## Proposal Process

### 1. Create Proposal

Create a YAML file in this directory:

```bash
cat > proposals/my-new-term.yaml <<EOF
name: "My New Term"
category: "Core Engine"
proposed_by: "my-name"
proposed_date: "$(date -I)"
status: "proposed"

definition: "Component that..."

rationale: "This term appears in..."

implementation:
  files:
    - "path/to/implementation.py"
EOF
```

### 2. Create GitHub Issue

Create issue with label `glossary-proposal`:

```markdown
**Proposal**: [Link to proposals/my-new-term.yaml]

**Term Name**: My New Term
**Category**: Core Engine

**Summary**: Brief description of why this term is needed

**Evidence**:
- Referenced in X files
- Mentioned in Y documents
- Part of Z initiative
```

### 3. Architecture Team Review

Team reviews weekly:
- ✅ Approve → Move to `draft`
- ❌ Reject → Add rejection note
- 🔄 Needs revision → Request changes

### 4. If Approved

Once approved, the term moves to `draft` status:

1. Tool adds to `.glossary-metadata.yaml` with `status: draft`
2. Proposer writes full definition in `glossary.md`
3. Architecture team reviews draft
4. If approved → `status: active`
5. Announcement in changelog

---

## Proposal Templates

### Core Engine Component

```yaml
name: "Component Name"
category: "Core Engine"
proposed_by: "developer-name"
proposed_date: "2025-11-25"
status: "proposed"

definition: "Component that [primary responsibility]."

rationale: |
  This component is central to [system area] but lacks documentation.
  Referenced in multiple modules.

implementation:
  files:
    - "core/engine/component.py"
  entry_points:
    - "Component.execute()"

related_terms:
  - term_id: TERM-ENGINE-001
    relationship: uses
```

### Error Detection Concept

```yaml
name: "Error Concept"
category: "Error Detection"
proposed_by: "developer-name"
proposed_date: "2025-11-25"
status: "proposed"

definition: "Process of [error handling behavior]."

rationale: |
  This error handling pattern is used across multiple plugins
  but not formally defined.

implementation:
  files:
    - "error/engine/concept.py"

related_terms:
  - term_id: TERM-ERROR-001
    relationship: implements
```

### Framework Pattern

```yaml
name: "Pattern Name"
category: "Framework"
proposed_by: "architecture-team"
proposed_date: "2025-11-25"
status: "proposed"

definition: "Design pattern that [purpose and benefit]."

rationale: |
  Part of UET framework alignment. Referenced in UET documentation
  but not in our glossary.

schema_refs:
  - "schema/uet/pattern.v1.json"

related_terms:
  - term_id: TERM-FRAME-001
    relationship: extends
```

---

## Proposal Status Values

| Status | Description | Next Step |
|--------|-------------|-----------|
| `proposed` | Awaiting review | Architecture team approval |
| `approved` | Approved, needs drafting | Write full definition |
| `draft` | Definition being written | Peer review |
| `rejected` | Not approved | Add rejection reason |
| `needs_revision` | Changes requested | Revise and resubmit |

---

## Review Criteria

### Must Have

- ✅ Clear, specific definition
- ✅ Category assignment
- ✅ Rationale for inclusion
- ✅ Evidence of usage (code refs, doc refs)
- ✅ At least 1 related term

### Nice to Have

- Implementation paths
- Usage examples
- Schema references
- Supporting evidence

### Common Rejection Reasons

- ❌ Too vague or general
- ❌ Already covered by existing term
- ❌ Not used in codebase
- ❌ Too implementation-specific
- ❌ Temporary/ephemeral concept

---

## Files in This Directory

```
proposals/
├── README.md                    # This file
├── circuit-breaker.yaml         # Example proposal
├── worker-health.yaml           # Example proposal
└── approved/                    # Approved but not yet drafted
    └── archived/                # Historical proposals
```

---

## Common Questions

### Q: How long does review take?
A: Weekly reviews, typically 1-2 weeks for decision.

### Q: Can I propose multiple terms at once?
A: Yes, but create separate files for each term.

### Q: What if my proposal is rejected?
A: You can revise and resubmit, or discuss with architecture team.

### Q: Can I start writing the definition before approval?
A: Yes, but approval is needed before adding to main glossary.

---

## Related

- [../scripts/README.md](../scripts/README.md) - Tool for adding terms
- [../docs/DOC_GLOSSARY_GOVERNANCE.md](../docs/DOC_GLOSSARY_GOVERNANCE.md) - Governance process
- [../GLOSSARY_SYSTEM_OVERVIEW.md](../GLOSSARY_SYSTEM_OVERVIEW.md) - System overview

---

**Status**: Ready for proposals  
**Contact**: Architecture team for questions
