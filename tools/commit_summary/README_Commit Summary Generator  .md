# Commit Summary Generator – Agent README (SSOT)

## Purpose (Authoritative)

This folder defines the **Single Source of Truth (SSOT)** and **only authorized generator** for automated Git commit summaries used by the pipeline.

It contains:

1. A **JSON Schema contract** that defines the exact machine-readable format of a valid commit summary.
2. A **PowerShell generator** that extracts Git history, classifies commits, computes risk, and produces a Markdown report whose embedded JSON **must strictly conform to the schema**.

No other tool, script, or agent is authorized to invent or modify the commit summary format outside this contract.

---

## Files in This Folder

### 1. `commit_summary.schema.json`  ✅ **FORMAT AUTHORITY (SSOT)**

**Role:**
This file is the **formal schema contract** for all commit summaries.

**It defines:**
- Required top-level metadata (`doc_type`, `schema_version`, `doc_id`)
- Time window structure
- Repository and branch metadata
- Aggregated statistics
- Risk classification
- Focus signal
- Full per-commit structure (hashes, authors, phases, subsystems, files, tests, risk, automation impact)

**Rules:**
- Every commit summary JSON **MUST validate** against this schema.
- If the PowerShell generator output violates this schema, the generator is considered **broken**.
- Any agent modifying the schema **must also update the generator logic**.

**This file is the immutable format authority.**

---

### 2. `generate_commit_summary.ps1` ✅ **OFFICIAL GENERATOR**

**Role:**
This script is the **only authorized producer** of commit summaries.

**It performs:**
- Time-window selection (`-Hours`, scheduled or on-demand)
- Branch selection
- Git commit extraction
- File-level diff analysis
- Test detection
- Pipeline detection
- Phase mapping
- Subsystem mapping
- Risk scoring
- Focus signal derivation
- Aggregated statistics
- JSON generation that must match `commit_summary.schema.json`
- Markdown report generation with embedded JSON payload

**This script is the execution implementation of the schema contract.**

---

## Execution Modes

The generator supports **two legal modes**, which must be reflected in `generated_by.mode`:

| Mode | Meaning |
|------|---------|
| `auto_6h` | Scheduled execution on a fixed interval |
| `on_demand` | Manual execution |

The schema enforces this.

---

## Required Execution Contract

When invoked, the generator **must**:

1. Determine:
   - Repo name
   - Default branch
   - Branches analyzed
   - Time window start & end
2. Collect commits strictly from Git history.
3. Deduplicate commits across branches.
4. Classify each commit into:
   - Phases
   - Subsystems
5. Detect:
   - Tests changed
   - Pipeline files changed
6. Compute:
   - Commit count
   - Author count
   - Files changed
   - Tests changed
   - Pipelines touched
7. Assign:
   - Per-commit risk
   - Overall risk
   - Automation impact
   - Focus signal
8. Emit:
   - A Markdown report
   - With a single embedded JSON block
   - That strictly validates against `commit_summary.schema.json`

---

## Validation Requirement (Agents)

Any AI agent operating in this folder **must always assume**:

- The JSON schema is the **truth**.
- The PowerShell script is the **only producer**.
- Human-written summaries are **not authoritative**.
- If the output does not validate against the schema, it is **invalid**.

Agents should perform schema validation after generation before downstream consumption.

---

## Allowed Agent Operations

✅ Modify generator to improve:
- Classification logic
- Phase / subsystem mapping
- Risk scoring heuristics
- Performance
- Output formatting

✅ Modify schema if:
- New fields are truly required
- Generator is updated simultaneously
- Downstream tools are informed

❌ NOT allowed:
- Inventing new summary formats outside this schema
- Emitting free-form summaries
- Bypassing JSON emission
- Creating alternate generators without explicit orchestration approval

---

## Design Intent Summary

This folder exists to guarantee that:

- Commit summaries are:
  - Deterministic
  - Machine-parsable
  - Auditable
  - Long-term stable
- Human prose is secondary.
- JSON is the primary truth.
- Scheduling and on-demand generation produce identical structure.

This is an **automation boundary and trust boundary**.

---

## Quick Command Pattern (Reference Only)

Example invocation pattern (not authoritative):

```powershell
.\generate_commit_summary.ps1 -Hours 12 -Mode on_demand -OutputPath ".\output\commit_summary_2025-12-09.md"
