# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the AI Development Pipeline project.

## What is an ADR?

An Architecture Decision Record (ADR) documents important architectural decisions made in the project, including:
- **Context:** What problem or situation triggered the decision
- **Decision:** What we decided to do
- **Rationale:** Why we made this decision
- **Consequences:** What results (positive and negative) from this decision
- **Alternatives:** What other options we considered and rejected

## Purpose

ADRs help AI agents and developers understand:
- **WHY** decisions were made, not just WHAT was implemented
- **Historical context** that led to current architecture
- **Rejected alternatives** to avoid proposing them again
- **Tradeoffs** accepted for the chosen approach

## Format

All ADRs follow the template in `template.md`. Each ADR is numbered sequentially and named descriptively.

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](0001-workstream-model-choice.md) | Workstream Model Choice | Accepted | 2025-11-22 |
| [0002](0002-hybrid-architecture.md) | Hybrid Architecture | Accepted | 2025-11-22 |
| [0003](0003-sqlite-state-storage.md) | SQLite State Storage | Accepted | 2025-11-22 |
| [0004](0004-section-based-organization.md) | Section-Based Organization | Accepted | 2025-11-22 |
| [0005](0005-python-primary-language.md) | Python Primary Language | Accepted | 2025-11-22 |
| [0006](0006-specifications-unified-management.md) | Specifications Unified Management | Accepted | 2025-11-22 |
| [0007](0007-error-plugin-architecture.md) | Error Plugin Architecture | Accepted | 2025-11-22 |
| [0008](0008-database-location-worktree.md) | Database Location Worktree | Accepted | 2025-11-22 |

## References

- [Phase K+ Plan](../../meta/plans/phase-K-plus-decision-context.md)
- [Architecture Documentation](../ARCHITECTURE.md)
- [Documentation Index](../DOCUMENTATION_INDEX.md)
