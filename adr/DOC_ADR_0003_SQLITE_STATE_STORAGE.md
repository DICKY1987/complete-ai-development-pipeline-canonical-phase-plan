---
status: canonical
doc_type: adr
module_refs: []
script_refs: []
doc_id: DOC-ARCH-ADR_0003_SQLITE_STATE_STORAGE-013
---

# ADR-0003: SQLite State Storage

**Status:** Accepted  
**Date:** 2025-11-22  
**Deciders:** System Architecture Team  
**Context:** Need persistent state storage for workstream execution tracking, job management, and error detection

---

## Decision

We will use **SQLite** as the primary state storage database, located at `.worktrees/pipeline_state.db` (configurable via `PIPELINE_DB_PATH` environment variable).

---

## Rationale

### Requirements Analysis

The pipeline needs to:
1. Track workstream execution state (pending, running, success, failure)
2. Store job queue and worker state
3. Persist error detection results and file hashes
4. Enable crash recovery and resume-from-checkpoint
5. Support concurrent reads (many) and writes (few)
6. Work across Windows, macOS, and Linux
7. Require zero external dependencies or server setup

### Why SQLite Fits

1. **Zero Configuration:** Embedded database, no server process needed
2. **Cross-Platform:** Works identically on Windows, macOS, Linux
3. **ACID Compliance:** Reliable transactions and crash recovery
4. **Proven Technology:** Battle-tested, used by browsers, mobile apps, embedded systems
5. **Single-Writer Model:** Matches our use case (one orchestrator writes, many readers)
6. **File-Based:** Easy backup, copy, and version control (when needed)
7. **Python Integration:** Excellent support via built-in `sqlite3` module

### Location Choice: `.worktrees/`

Database is stored in `.worktrees/` directory because:
- **Git-Ignored:** State is local, not committed to version control
- **Worktree Isolation:** Each git worktree has independent state
- **Discoverable:** Predictable location for tooling and scripts

---

## Consequences

### Positive

- **Developer Experience:** No database setup required - works immediately
- **Portability:** Entire project state is a single file
- **Backup Simplicity:** Just copy the `.db` file
- **Testing Friendly:** Each test can use isolated in-memory database
- **Low Overhead:** No network calls, minimal resource usage
- **Built-In Tooling:** Can inspect with `sqlite3` CLI or GUI tools

### Negative

- **Concurrency Limits:** Single writer at a time (not a problem for our use case)
- **Network Access:** Cannot share database across machines without file sync
- **Scaling Ceiling:** Not suitable for >1GB databases or high-concurrency writes
- **No Built-In Replication:** Must handle backups manually

### Neutral

- **Backup Strategy Needed:** No automatic backup like managed databases
- **File Locking:** OS-level file locks can be tricky on network filesystems

---

## Alternatives Considered

### Alternative 1: PostgreSQL

**Description:** Industry-standard relational database with advanced features

**Pros:**
- Excellent concurrency support
- Rich feature set (JSON, full-text search, etc.)
- Horizontal scaling via replication

**Rejected because:**
- Requires separate server process and configuration
- Additional deployment complexity for local development
- Network overhead for local operations
- Overkill for single-writer, low-concurrency use case
- Dependency installation burden (Windows users especially)

### Alternative 2: Redis

**Description:** In-memory key-value store with persistence

**Pros:**
- Very fast for simple operations
- Built-in pub/sub for event notifications
- Good for job queues

**Rejected because:**
- Requires separate server process
- Less suited for relational data (workstreams have complex relationships)
- Memory-first architecture wastes resources for infrequently-accessed data
- Query capabilities are limited compared to SQL

### Alternative 3: JSON Files

**Description:** Store state in JSON files in `.worktrees/state/`

**Pros:**
- No database dependency
- Human-readable and easy to inspect
- Simple to version control if needed

**Rejected because:**
- No ACID guarantees - crashes can corrupt state
- No concurrent access control (race conditions likely)
- Poor query performance (must load entire file)
- No indexing or efficient lookups
- Difficult to handle complex relationships

### Alternative 4: DuckDB

**Description:** Embedded analytical database (similar to SQLite but optimized for analytics)

**Pros:**
- Excellent for analytical queries and aggregations
- Great Python integration
- In-process like SQLite

**Rejected because:**
- Less mature than SQLite (fewer years in production)
- Optimized for OLAP (analytics), but we need OLTP (transactions)
- Less tooling support for inspection and debugging
- Not as ubiquitous as SQLite (installation burden)

---

## Related Decisions

- [ADR-0001: Workstream Model Choice](0001-workstream-model-choice.md) - What we're storing
- [ADR-0008: Database Location Worktree](0008-database-location-worktree.md) - Why `.worktrees/`
- [ADR-0004: Section-Based Organization](0004-section-based-organization.md) - Code organization

---

## References

- **Schema:** `schema/migrations/` (SQL migration files)
- **Database Module:** `core/state/db.py`
- **State Machine:** `docs/state_machine.md`
- **Configuration:** `PIPELINE_DB_PATH` environment variable

---

## Notes

### Database Schema Management

We use a simple migration system:
- Migrations in `schema/migrations/*.sql`
- Version tracked in `schema_version` table
- Applied automatically on first run

### Concurrency Model

Our use case is **single-writer, many-readers:**
- **Writer:** Orchestrator/engine updates state as steps execute
- **Readers:** UI modes query state for display

SQLite handles this well with:
- Write-Ahead Logging (WAL mode) for better concurrency
- Readers don't block writers
- Short write transactions minimize lock contention

### When to Consider Migration

We would consider migrating to PostgreSQL if:
- Multiple orchestrators need to write simultaneously (multi-machine execution)
- Database size exceeds 10GB
- Complex queries become performance bottlenecks
- Need for advanced features (full-text search, JSON indexing, etc.)

As of 2025-11-22, none of these conditions are expected.

### Backup Strategy

Users should backup `.worktrees/pipeline_state.db` before:
- Major version upgrades
- Schema migrations
- Long-running critical workflows

Simple backup:
```bash
cp .worktrees/pipeline_state.db .worktrees/pipeline_state.db.backup
```

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-22 | Initial ADR created as part of Phase K+ | GitHub Copilot |
