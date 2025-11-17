# Module Interface Definitions

This document defines the public interfaces and contracts for each module in the AI Development Pipeline.

## Module Dependency Graph

```
┌──────────┐
│  utils   │ (Foundation - no dependencies)
└────┬─────┘
     │
     ├─────────┐
     │         │
┌────▼─────┐ ┌▼────────┐
│ plugins  │ │ pipeline │ (Can depend on utils)
└──────────┘ └──────────┘
```

**Dependency Rules:**
- `utils` has NO internal dependencies (stdlib only)
- `plugins` depends on `utils` only
- `pipeline` depends on `utils` only (plugins are invoked via subprocess)
- NO circular dependencies allowed

## Utils Module Interface

**Location:** `src/utils/`

**Purpose:** Foundation layer providing shared utilities with no business logic.

### Public Functions

```python
# Environment management
def scrub_env(base: Dict[str, str] | None = None) -> Dict[str, str]
    """Sanitize environment variables for subprocess execution."""

# File hashing
def sha256_file(path: Path) -> str
    """Compute SHA256 hash of file contents."""

# Time utilities
def utc_now_iso() -> str
    """Return current UTC time in ISO 8601 format."""

def new_run_id() -> str
    """Generate unique run identifier (ULID or timestamp)."""
```

### Public Types

```python
@dataclass
class PluginIssue:
    """Normalized issue from plugin execution."""
    tool: str
    path: str
    line: int | None
    column: int | None
    code: str | None
    category: str  # style|syntax|type|security|test_failure
    severity: str  # error|warning|info
    message: str

@dataclass
class PluginResult:
    """Standardized result from plugin execution."""
    plugin_id: str
    success: bool
    issues: List[PluginIssue]
    stdout: str
    stderr: str
    returncode: int
```

### Dependencies
- External: None (stdlib only)
- Internal: None

### Stability
- **Stable** - Breaking changes require major version bump
- Types are part of the public API contract

---

## Plugins Module Interface

**Location:** `src/plugins/`

**Purpose:** Extensible plugin ecosystem for tool integrations.

### Plugin Contract

Every plugin MUST implement:

```python
class PluginClass:
    """Plugin implementation."""
    
    plugin_id: str  # Unique identifier (e.g., "python_ruff")
    name: str       # Human-readable name
    manifest: dict  # Plugin metadata (requires, success_codes, etc.)
    
    def check_tool_available(self) -> bool:
        """Check if the external tool is installed."""
        
    def build_command(self, file_path: Path) -> List[str]:
        """Build command-line arguments for tool execution."""
        
    def execute(self, file_path: Path) -> PluginResult:
        """Execute tool and return normalized result."""

def register():
    """Return plugin instance for registration."""
    return PluginClass()
```

### Plugin Execution Contract

**Environment:**
- Use `scrub_env()` to sanitize environment
- Set `cwd=file_path.parent` for relative paths
- Use `shell=False` for security

**Timeouts:**
- Default: 120 seconds
- Extended: 180 seconds (for semgrep, gitleaks)

**Return Codes:**
- Fix plugins: `[0]` only
- Lint plugins: `[0, 1]` (1 = issues found)
- Must be defined in `manifest["success_codes"]`

**Output Parsing:**
- Parse tool output to `List[PluginIssue]`
- Normalize severity and category
- Handle parse failures gracefully

### Dependencies
- External: Tool-specific binaries
- Internal: `src.utils.env`, `src.utils.types`

### Stability
- **Extensible** - New plugins can be added without breaking existing code
- Plugin contract is stable
- Individual plugins are independent

---

## Pipeline Module Interface

**Location:** `src/pipeline/`

**Purpose:** Core orchestration and workflow execution.

### Public Functions

```python
# Orchestration
def run_workstream(
    run_id: str,
    ws_id: str,
    bundle_obj: WorkstreamBundle,
    context: Optional[Mapping[str, Any]] = None
) -> Dict[str, Any]:
    """Execute EDIT → STATIC → RUNTIME for a single workstream."""

def run_single_workstream_from_bundle(
    ws_id: str,
    run_id: Optional[str] = None,
    context: Optional[Mapping[str, Any]] = None
) -> Dict[str, Any]:
    """Load bundle by ID and execute workstream."""

# Bundle management
def load_and_validate_bundles() -> List[WorkstreamBundle]:
    """Load and validate all workstream bundles from directory."""

# Tool execution
def run_tool(
    tool_id: str,
    variables: Dict[str, Any],
    run_id: Optional[str] = None,
    ws_id: Optional[str] = None
) -> ToolResult:
    """Execute external tool via adapter layer."""
```

### Public Types

```python
@dataclass(frozen=True)
class WorkstreamBundle:
    """Workstream definition loaded from JSON."""
    id: str
    openspec_change: str
    ccpm_issue: str | int
    gate: int
    files_scope: Tuple[str, ...]
    files_create: Tuple[str, ...]
    tasks: Tuple[str, ...]
    acceptance_tests: Tuple[str, ...]
    depends_on: Tuple[str, ...]
    tool: str
    circuit_breaker: Mapping[str, Any] | None
    metadata: Mapping[str, Any] | None

@dataclass
class ToolResult:
    """Result from external tool execution."""
    tool_id: str
    command_line: str
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool
    started_at: str
    completed_at: str
    duration_sec: float
    success: bool
```

### Internal Components

These are NOT part of the public API and may change:
- `db.py`, `db_sqlite.py` - Database operations
- `circuit_breakers.py` - Failure detection
- `prompts.py` - AI integration
- `worktree.py` - Git worktree management
- `error_*.py` - Error tracking and recovery

### Dependencies
- External: jsonschema, Jinja2, sqlite3
- Internal: `src.utils`

### Stability
- **Evolving** - Public API is stabilizing
- Core orchestration functions are stable
- Internal components may change

---

## Module Communication Patterns

### Pipeline → Tools (via subprocess)

```python
# Pipeline executes tools via subprocess, not direct import
from src.pipeline import run_tool

result = run_tool("pytest", {"repo_root": "/path/to/repo"})
```

### Pipeline → Plugins (via error engine)

```python
# Error pipeline discovers and loads plugins dynamically
from src.pipeline.agent_coordinator import run_parallel

results = run_parallel(
    python_files=["app.py"],
    plugin_ids=["python_ruff", "python_black_fix"]
)
```

### Any Module → Utils (direct import)

```python
# All modules can import utils directly
from src.utils import scrub_env, PluginResult
```

---

## Architectural Constraints

### 1. No Circular Dependencies
- Modules form a DAG (Directed Acyclic Graph)
- Violations detected by import-time errors
- Validated by architectural tests

### 2. Interface Segregation
- Modules expose minimal public APIs via `__init__.py`
- Internal implementation details are hidden
- Clients depend on abstractions, not implementations

### 3. Dependency Inversion
- High-level modules (pipeline) depend on low-level abstractions (tool profiles)
- Concrete implementations (plugins) register themselves
- No tight coupling to specific tools

### 4. Single Responsibility
- Each module has one primary purpose
- Related functionality is cohesive
- Unrelated functionality is separated

---

## Testing Contracts

### Unit Tests
- Test modules in isolation
- Mock external dependencies
- Verify public API behavior

### Integration Tests
- Test cross-module interactions
- Verify contracts are honored
- Test end-to-end workflows

### Architectural Tests
- Validate dependency rules
- Check for circular imports
- Verify public API stability

---

## Versioning

### API Version: 1.0

**Stability Guarantees:**
- `utils` module API is stable (breaking changes = major version)
- Plugin contract is stable (new optional fields allowed)
- Pipeline public API is evolving (minor changes allowed)

**Deprecation Policy:**
- Deprecated functions will emit warnings for 1 minor version
- Breaking changes announced in CHANGELOG
- Migration guides provided for major changes

---

## Extension Points

### Adding New Plugins
1. Create plugin directory under `src/plugins/<plugin_name>/`
2. Implement plugin contract in `plugin.py`
3. Add `register()` function
4. Plugin is automatically discovered

### Adding New Pipeline Steps
1. Add step function to appropriate module
2. Export via `__init__.py` if public
3. Document in module docstring
4. Add tests

### Adding New Utilities
1. Add function to appropriate utils module
2. Export via `src/utils/__init__.py`
3. Document function contract
4. Add unit tests

---

## References

- **Architecture Overview:** `docs/ARCHITECTURE.md`
- **Modular Architecture Guide:** `docs/MODULAR_ARCHITECTURE.md`
- **Plugin Ecosystem:** `src/plugins/README.md`
- **Repository Guidelines:** `AGENTS.md`
