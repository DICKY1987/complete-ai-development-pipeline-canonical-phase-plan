---
doc_id: DOC-GUIDE-DEPRECATED-1135
---

# DEPRECATED - Navigation Documents Archived

**Date**: 2025-11-23  
**Reason**: Superseded by consolidated navigation system

---

## What Happened

These navigation documents have been archived as part of the **AI Navigation Enhancement v2** project (Phase 2, WS-005).

## Why Were They Archived?

The repository had **6+ overlapping navigation documents** with contradictory or duplicate information. This caused:
- Confusion for both AI tools and humans
- Maintenance burden (updating multiple docs)
- Inconsistent navigation guidance

## Replacement System

**New Navigation Structure** (consolidated in Phase 1 & 2):

### For AI Tools
- **[.ai-context.md](../../../.ai-context.md)** - Primary AI orientation (30 seconds)
- **[CODEBASE_INDEX.yaml](../../../CODEBASE_INDEX.yaml)** - Machine-readable structure
- **Module `.ai-module-manifest` files** - Per-module AI specs

### For Humans
- **[NAVIGATION.md](../../../NAVIGATION.md)** - Unified navigation hub
- **[README.md](../../../README.md)** - Main entry point
- **[QUICK_START.md](../../../QUICK_START.md)** - Task-based guide

### Focused Indexes (Retained)
- **[API_INDEX.md](../../../API_INDEX.md)** - All APIs
- **[EXECUTION_INDEX.md](../../../EXECUTION_INDEX.md)** - Execution flows
- **[DEPENDENCY_INDEX.md](../../../DEPENDENCY_INDEX.md)** - Dependencies

---

## Archived Documents

### MASTER_NAVIGATION_INDEX.md
- **Purpose**: Comprehensive navigation index
- **Status**: Superseded by NAVIGATION.md
- **Archived**: 2025-11-23

### DIRECTORY_GUIDE.md
- **Purpose**: Directory structure walkthrough
- **Status**: Merged into NAVIGATION.md
- **Archived**: 2025-11-23

---

## Migration Guide

**If you were using**:
- `MASTER_NAVIGATION_INDEX.md` → Use **[NAVIGATION.md](../../../NAVIGATION.md)**
- `DIRECTORY_GUIDE.md` → Use **[NAVIGATION.md](../../../NAVIGATION.md)** (By Intent or By Topic sections)

**If you need historical reference**:
- These files remain in this archive directory
- Do NOT link to them in new documentation
- Use the new navigation system instead

---

## Benefits of New System

### Reduced Redundancy
- **Before**: 6+ navigation docs with overlapping content
- **After**: 1 primary navigation hub + focused indexes

### Clearer Roles
- **AI tools**: `.ai-context.md` (instant orientation)
- **Humans**: `NAVIGATION.md` (comprehensive navigation)
- **Specialized**: Focused indexes for specific needs

### Easier Maintenance
- **Before**: Update info in 4-6 places
- **After**: Update info in 1 place

### Faster Navigation
- **Before**: 4-5 hops to find information
- **After**: ≤2 hops to find anything

---

## For AI Tools

**DO NOT**:
- Link to files in this archive directory
- Reference MASTER_NAVIGATION_INDEX.md or DIRECTORY_GUIDE.md
- Suggest these as navigation resources

**DO**:
- Use [NAVIGATION.md](../../../NAVIGATION.md) for navigation guidance
- Use [.ai-context.md](../../../.ai-context.md) for quick orientation
- Use focused indexes for specific lookups

---

**Related**: See [PH-AI-NAV-002 Phase Plan](../../../devdocs/phases/ai-navigation-v2/PHASE_PLAN.md) for full context.
