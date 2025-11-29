# Metrics Directory

**Purpose**: Pattern automation database and SQL migration scripts.

**Status**: Active

---

## Contents

| File | Description |
|------|-------------|
| `pattern_automation.db` | SQLite database for pattern automation metrics |
| `004_pattern_automation.sql` | Database migration script (tables and schema) |
| `rollback_pattern_automation.sql` | Rollback script for migration |

---

## Database Schema

The `pattern_automation.db` database tracks:

- **Execution logs** - Pattern execution history
- **Performance metrics** - Timing and resource usage
- **Detection results** - Auto-detected patterns
- **Anti-patterns** - Failure pattern tracking

---

## Usage

### Query the Database

```bash
sqlite3 pattern_automation.db
```

### Apply Migration

```bash
sqlite3 pattern_automation.db < 004_pattern_automation.sql
```

### Rollback Migration

```bash
sqlite3 pattern_automation.db < rollback_pattern_automation.sql
```

---

## Integration

The database is used by:

- `../automation/integration/` - Orchestrator hooks log to this database
- `../automation/analyzers/` - Performance analyzers read from this database

See `../automation/integration/README.md` for hook setup.

---

## Related

- `../automation/` - Automation utilities
- `../pattern_event_system/` - Event system documentation
