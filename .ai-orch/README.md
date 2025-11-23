# AI Orchestration Configuration

## Purpose

This directory contains machine-readable specifications and configurations for AI-assisted development, validation, and orchestration workflows.

## Structure

```
.ai-orch/
└── checklists/
    ├── repo_checklist.json      # Main repository validation checklist
    └── (future: per-phase checklists, etc.)
```

## What's Here

### `checklists/`

**Machine-readable validation and compliance checklists.**

- **`repo_checklist.json`** - Repository-wide validation requirements
  - Consolidates all validation logic from scattered scripts
  - Defines requirement IDs (ACS-*, STATE-OBS-*, AUDIT-*, etc.)
  - Specifies check types and parameters
  - Used by `scripts/validate/validate_repo_checklist.ps1`

**Schema**: See `docs/operations/REPO_CHECKLIST.md`

## Why This Directory Exists

The `.ai-orch/` directory centralizes **AI orchestration configuration** separately from:

- **`.meta/`** - AI context and generated artifacts
- **`config/`** - Application configuration
- **`schema/`** - Data schemas
- **`docs/`** - Human-readable documentation

This separation enables:
- **Version control**: AI orchestration specs tracked separately
- **Tooling**: Tools can discover AI orchestration by convention
- **Clarity**: Clear boundary between AI config and app config
- **Extensibility**: Room for future AI orchestration needs

## Related Documentation

- **`docs/operations/REPO_CHECKLIST.md`** - Checklist system guide
- **`docs/operations/AUDIT_TRAIL.md`** - Audit trail documentation
- **`ai_policies.yaml`** (repo root) - AI edit policies
- **`QUALITY_GATE.yaml`** (repo root) - Quality gates

## Future Additions

This directory may grow to include:

- **Phase execution configs** - UET phase definitions
- **Workflow orchestration** - Multi-tool coordination
- **Prompt templates** - Structured prompts for AI tools
- **Context profiles** - AI context configurations
- **Capability registries** - Available tool capabilities

## Version

**Structure Version**: 1.0.0  
**Created**: 2025-11-23
