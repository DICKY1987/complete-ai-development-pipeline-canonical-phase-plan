---
status: canonical
doc_type: adr
module_refs: []
script_refs: []
doc_id: DOC-ARCH-ADR_0007_ERROR_PLUGIN_ARCHITECTURE-007
---

# ADR-0007: Error Plugin Architecture

**Status:** Accepted  
**Date:** 2025-11-22  
**Deciders:** System Architecture Team  
**Context:** Need extensible system for detecting and reporting errors across different languages, tools, and quality dimensions

---

## Decision

We will implement error detection as a **plugin-based architecture** where each detection capability is an independent plugin discovered dynamically via `manifest.json` files.

---

## Rationale

### Requirements for Error Detection

The system must:
1. Support **multiple languages** (Python, JavaScript, PowerShell, etc.)
2. Support **multiple tools** (ruff, mypy, eslint, psscriptanalyzer, etc.)
3. Support **multiple dimensions** (syntax, style, security, performance)
4. Be **extensible** - easy to add new detectors without core changes
5. Enable **incremental detection** - only scan changed files
6. Allow **parallel execution** - run multiple detectors concurrently
7. Support **auto-fixing** - some plugins can fix issues they detect

### Plugin Architecture Benefits

1. **Isolation:** Plugin failures don't crash the entire error engine
2. **Independent Development:** Teams can develop plugins separately
3. **Selective Loading:** Only load plugins for languages/tools in use
4. **Easy Testing:** Each plugin has its own test suite
5. **Clear Interface:** Plugins implement `parse()` and optional `fix()`
6. **Discovery:** Manifest files enable automatic plugin registration

---

## Consequences

### Positive

- **Extensibility:** Add new detectors without modifying error engine
- **Maintainability:** Each plugin is self-contained and testable
- **Performance:** Can skip irrelevant plugins (e.g., JS plugins for Python-only project)
- **Parallel Execution:** Plugins run concurrently for faster scans
- **User Choice:** Users can enable/disable specific plugins
- **Auto-Fix Capability:** Plugins that support fixing can run in fix mode

### Negative

- **Discovery Overhead:** Must scan filesystem for `manifest.json` files
- **Interface Complexity:** Plugins must conform to expected interface
- **Debugging:** Errors in plugins require looking at plugin code

### Neutral

- **Manifest Maintenance:** Each plugin needs a `manifest.json`
- **Versioning:** Plugin API must be versioned for backward compatibility

---

## Alternatives Considered

### Alternative 1: Monolithic Error Detector

**Description:** Single module with all detection logic built-in

**Pros:**
- Simpler implementation initially
- No plugin discovery overhead
- Easier to test as a unit

**Rejected because:**
- Becomes unmaintainable as detectors grow
- Adding new language/tool requires core changes
- Tight coupling between unrelated detection logic
- Can't disable specific detectors easily

### Alternative 2: Tool-Specific Scripts

**Description:** Separate scripts for each tool (e.g., `run_ruff.sh`, `run_eslint.sh`)

**Pros:**
- Very simple, no abstractions
- Easy to understand

**Rejected because:**
- No unified interface for reporting errors
- Duplicate logic for file scanning, result parsing
- Hard to run tools in parallel
- No standard format for results

### Alternative 3: Configuration-Based Detection

**Description:** Configure tools in YAML/JSON, no plugin code

**Pros:**
- Declarative configuration
- No custom code needed

**Rejected because:**
- Limited to tools with standard output formats
- Can't handle custom parsing logic
- No support for auto-fixing
- Difficult to add preprocessing steps

---

## Related Decisions

- [ADR-0004: Section-Based Organization](0004-section-based-organization.md) - Why `error/` section exists
- [ADR-0005: Python Primary Language](0005-python-primary-language.md) - Plugin implementation language

---

## References

- **Error Engine:** `error/engine/error_engine.py`
- **Plugin Interface:** `error/engine/plugin_interface.py`
- **Plugin Directory:** `error/plugins/`
- **Example Plugin:** `error/plugins/python_ruff/`
- **Plugin Manager:** `error/engine/plugin_manager.py`

---

## Notes

### Plugin Structure

Each plugin is a directory with:
```
error/plugins/python_ruff/
├── manifest.json       # Plugin metadata
├── plugin.py           # Entry point (parse, fix functions)
├── requirements.txt    # Plugin-specific dependencies (optional)
└── tests/             # Plugin tests
    └── test_plugin.py
```

### Manifest Format

```json
{
  "plugin_id": "python_ruff",
  "name": "Ruff Python Linter",
  "version": "1.0.0",
  "supported_languages": ["python"],
  "file_patterns": ["*.py"],
  "capabilities": ["parse", "fix"],
  "dependencies": ["ruff"],
  "entry_point": "plugin.py"
}
```

### Plugin Interface

Plugins must implement:

```python
def parse(file_path: str, content: str) -> List[ErrorRecord]:
    """
    Parse file and return detected errors.
    
    Args:
        file_path: Path to file being analyzed
        content: File content (for tools that accept stdin)
    
    Returns:
        List of ErrorRecord objects
    """
    pass

def fix(file_path: str) -> FixResult:
    """
    (Optional) Attempt to fix errors in file.
    
    Args:
        file_path: Path to file to fix
    
    Returns:
        FixResult with success status and changes made
    """
    pass
```

### Plugin Discovery

Error engine discovers plugins:
1. Scan `error/plugins/` for subdirectories
2. Look for `manifest.json` in each subdirectory
3. Validate manifest against schema
4. Load plugin if applicable to current project
5. Register in plugin registry

### Incremental Detection

Plugins support incremental detection:
- **File Hashing:** Error engine tracks SHA256 hash of each file
- **Skip Unchanged:** If file hash hasn't changed, skip re-scanning
- **Changed Files Only:** Plugins receive list of modified files
- **Cache Results:** Previous results cached in database

### Current Plugins (as of 2025-11-22)

| Plugin | Language | Tool | Capabilities |
|--------|----------|------|--------------|
| `python_ruff` | Python | ruff | parse, fix |
| `python_mypy` | Python | mypy | parse |
| `javascript_eslint` | JavaScript | eslint | parse, fix |
| `security_gitleaks` | All | gitleaks | parse |
| `generic_codespell` | All | codespell | parse, fix |

### Adding a New Plugin

1. Create directory: `error/plugins/your_plugin/`
2. Add `manifest.json` with metadata
3. Implement `plugin.py` with `parse()` function
4. (Optional) Implement `fix()` for auto-fixing
5. Add tests: `tests/test_plugin.py`
6. Document in `error/plugins/README.md`

No core code changes needed!

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-22 | Initial ADR created as part of Phase K+ | GitHub Copilot |
