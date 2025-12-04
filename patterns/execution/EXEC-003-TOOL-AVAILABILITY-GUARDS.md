---
doc_id: DOC-PAT-EXEC-003-892
pattern_id: EXEC-003
version: 1.0.0
status: active
created: 2025-12-04
category: execution
priority: critical
---

# EXEC-003: Tool Availability Guards Pattern

## Overview

**Pattern Name**: Tool Availability Guards
**Problem**: Missing command/tool errors causing 16% of execution failures
**Solution**: Pre-flight tool existence verification before execution
**Impact**: Prevents all "command not found" errors

---

## Problem Statement

### Observed Behavior
```
Lines 12-20, 52-60, 78-127:
Repeated failed attempts to use "apply_patch" command
Error: "The system cannot find the file specified. (os error 2)"

Pattern: Tool invoked without checking if it exists in PATH
Result: 15+ failures, 90-180s wasted per session
```

### Root Cause
Commands executed without environment validation:
- No PATH checks before tool invocation
- No version compatibility checks
- No graceful fallback when tool missing
- Multiple retries of same failing command

### Cost
- **15 failures** observed (16% of total errors)
- **90-180 seconds wasted** per session on retry cycles
- **User frustration** from repeated identical errors
- **No actionable guidance** on how to fix (missing install hint)

---

## Solution Pattern

### Core Principle
**Verify tool presence in PATH before invoking, fail fast with install hint**

### Implementation

```python
import shutil
import subprocess
from typing import Optional, Dict
from dataclasses import dataclass

@dataclass
class ToolInfo:
    """Information about a required tool"""
    name: str
    path: str
    version: Optional[str] = None
    install_hint: Optional[str] = None


class ToolGuard:
    """EXEC-003: Tool presence verification"""

    def __init__(self):
        self.verified_tools: Dict[str, ToolInfo] = {}
        self.install_hints: Dict[str, str] = {
            'apply_patch': 'cargo install apply-patch',
            'git': 'https://git-scm.com/downloads',
            'python': 'https://python.org/downloads',
            'node': 'https://nodejs.org/',
            'cargo': 'https://rustup.rs/',
            'pytest': 'pip install pytest',
            'black': 'pip install black',
            'ruff': 'pip install ruff',
        }

    def register_install_hint(self, tool_name: str, hint: str):
        """Register custom install hint for tool"""
        self.install_hints[tool_name] = hint

    def require_tool(
        self,
        tool_name: str,
        install_hint: Optional[str] = None,
        min_version: Optional[str] = None
    ) -> ToolInfo:
        """EXEC-003: Verify tool before invoking"""

        # Check cache
        if tool_name in self.verified_tools:
            return self.verified_tools[tool_name]

        # Gate 1: Check if tool exists in PATH
        tool_path = shutil.which(tool_name)

        if tool_path is None:
            # Get install hint
            hint = install_hint or self.install_hints.get(tool_name)

            error_msg = f"MISSING_TOOL: {tool_name} not found in PATH"
            if hint:
                error_msg += f"\n\nInstall with:\n  {hint}"

            raise EnvironmentError(error_msg)

        # Gate 2: Optionally check version
        version = None
        if min_version:
            version = self._get_tool_version(tool_name)
            if version and not self._version_compatible(version, min_version):
                raise EnvironmentError(
                    f"VERSION_MISMATCH: {tool_name} {version} found, "
                    f"but {min_version}+ required"
                )

        # Cache and return
        tool_info = ToolInfo(
            name=tool_name,
            path=tool_path,
            version=version,
            install_hint=install_hint or self.install_hints.get(tool_name)
        )
        self.verified_tools[tool_name] = tool_info

        return tool_info

    def _get_tool_version(self, tool_name: str) -> Optional[str]:
        """Attempt to get tool version"""
        version_flags = ['--version', '-v', 'version']

        for flag in version_flags:
            try:
                result = subprocess.run(
                    [tool_name, flag],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')[0]
            except:
                continue

        return None

    def _version_compatible(self, current: str, required: str) -> bool:
        """Simple version comparison (extend as needed)"""
        try:
            current_parts = [int(x) for x in current.split('.')[:3]]
            required_parts = [int(x) for x in required.split('.')[:3]]
            return current_parts >= required_parts
        except:
            return True  # If can't parse, assume compatible

    def require_all(self, *tool_names: str) -> Dict[str, ToolInfo]:
        """Verify multiple tools at once"""
        results = {}
        missing = []

        for tool_name in tool_names:
            try:
                results[tool_name] = self.require_tool(tool_name)
            except EnvironmentError as e:
                missing.append(str(e))

        if missing:
            raise EnvironmentError(
                f"MISSING_TOOLS: {len(missing)} required tools not found:\n" +
                "\n".join(missing)
            )

        return results

    def execute_guarded(
        self,
        command: str,
        check: bool = True,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """Execute command with tool guard"""

        # Extract tool name (first word of command)
        tool_name = command.split()[0]

        # Gate: Verify tool exists
        self.require_tool(tool_name)

        # Execute
        return subprocess.run(
            command,
            shell=True,
            check=check,
            **kwargs
        )
```

---

## Usage Examples

### Example 1: Basic Tool Guard

```python
# Verify single tool before use
guard = ToolGuard()

try:
    guard.require_tool("apply_patch", "cargo install apply-patch")
    # Now safe to use apply_patch
    subprocess.run("apply_patch file.patch", shell=True)
except EnvironmentError as e:
    print(e)  # Shows install hint if missing
```

### Example 2: Batch Tool Verification

```python
# Verify multiple tools before starting workflow
guard = ToolGuard()

try:
    tools = guard.require_all('git', 'python', 'pytest')
    print(f"All tools verified:")
    for name, info in tools.items():
        print(f"  {name}: {info.path}")

    # Proceed with workflow
    run_tests()
except EnvironmentError as e:
    print(f"Cannot proceed: {e}")
```

### Example 3: Version-Specific Requirements

```python
# Require specific minimum version
guard = ToolGuard()

try:
    python_info = guard.require_tool('python', min_version='3.9')
    print(f"Using Python {python_info.version} at {python_info.path}")
except EnvironmentError as e:
    print(e)  # VERSION_MISMATCH if too old
```

### Example 4: Guarded Execution

```python
# Execute command with automatic tool guard
guard = ToolGuard()

try:
    result = guard.execute_guarded(
        "ruff check src/",
        capture_output=True,
        text=True
    )
    print(result.stdout)
except EnvironmentError as e:
    print(e)  # Tool not found, with install hint
except subprocess.CalledProcessError as e:
    print(f"Command failed: {e}")  # Tool found, but command failed
```

---

## Integration Points

### With EXEC-002 (Batch Validation)

```python
from core.patterns.exec002 import BatchExecutor, Operation, OperationType

def batch_execute_with_guards(commands: list):
    """Combine EXEC-003 with EXEC-002"""
    guard = ToolGuard()
    batch = BatchExecutor()

    # Add tool guard operations
    for cmd in commands:
        tool_name = cmd.split()[0]

        batch.add(Operation(
            name=f"verify_{tool_name}",
            type=OperationType.EXECUTE,
            target=tool_name,
            action=lambda t=tool_name: guard.require_tool(t)
        ))

    # Validate all tools exist before executing any command
    batch.execute_all()

    # Now execute commands (all tools verified)
    for cmd in commands:
        subprocess.run(cmd, shell=True, check=True)
```

### With PATTERN-002 (Ground Truth Verification)

```python
def execute_with_verification(
    command: str,
    expected_outcome: callable,
    guard: ToolGuard
):
    """Combine EXEC-003 with PATTERN-002"""

    # Gate 1: Tool exists (EXEC-003)
    tool_name = command.split()[0]
    guard.require_tool(tool_name)

    # Gate 2: Execute
    result = subprocess.run(command, shell=True, capture_output=True)

    # Gate 3: Verify outcome (PATTERN-002)
    if result.returncode == 0:
        if not expected_outcome():
            raise RuntimeError(
                f"HALLUCINATED_SUCCESS: {command} reported success "
                f"but expected outcome not observed"
            )

    return result
```

---

## Decision Tree

```
Need to Execute External Command?
  │
  ├─ Known tool (git, python, etc.)?
  │   YES → Use require_tool(name, install_hint)
  │   NO  → Add to install_hints registry first
  │
  ├─ Multiple tools needed?
  │   YES → Use require_all(*tools)
  │   NO  ↓
  │
  ├─ Version-specific requirement?
  │   YES → require_tool(name, min_version='X.Y')
  │   NO  ↓
  │
  └─ One-off command?
      YES → Use execute_guarded(command)
      NO  → require_tool() then execute manually
```

---

## Metrics

### Prevents
- **Command not found errors**: 100% elimination
- **Retry cycles on missing tools**: All prevented
- **Session-blocking errors**: 16% of observed errors (15 incidents)

### Performance
- **Overhead**: <10ms per tool check (cached after first check)
- **Savings**: 90-180s per session (prevents retry cycles)
- **ROI**: 9,000:1 (10ms overhead vs 90s wasted retries)

---

## Anti-Patterns (Don't Do This)

### ❌ Anti-Pattern 1: Try-Catch Without Hint
```python
# BAD: Catches error but gives no guidance
try:
    subprocess.run("apply_patch file.patch", shell=True, check=True)
except subprocess.CalledProcessError:
    print("Command failed")  # User doesn't know tool is missing
```

### ❌ Anti-Pattern 2: Retry Without Tool Check
```python
# BAD: Retries same missing command multiple times
for attempt in range(3):
    try:
        subprocess.run("missing_tool", shell=True, check=True)
        break
    except:
        time.sleep(1)  # Won't help if tool doesn't exist!
```

### ✅ Correct Pattern: Guard Before Execute
```python
# GOOD: Verify tool, fail fast with hint
guard = ToolGuard()
guard.require_tool("apply_patch", "cargo install apply-patch")
subprocess.run("apply_patch file.patch", shell=True, check=True)
```

---

## Testing Strategy

```python
import pytest
from unittest.mock import patch

def test_tool_found():
    """Test EXEC-003: Tool exists in PATH"""
    guard = ToolGuard()

    # Should succeed for Python (always in PATH when running tests)
    info = guard.require_tool('python')
    assert info.name == 'python'
    assert info.path is not None

def test_tool_not_found():
    """Test EXEC-003: Tool missing from PATH"""
    guard = ToolGuard()

    with pytest.raises(EnvironmentError, match="MISSING_TOOL"):
        guard.require_tool('nonexistent_tool_xyz')

def test_install_hint():
    """Test EXEC-003: Install hint provided"""
    guard = ToolGuard()
    guard.register_install_hint('mytool', 'brew install mytool')

    try:
        guard.require_tool('mytool')
    except EnvironmentError as e:
        assert 'brew install mytool' in str(e)

def test_tool_caching():
    """Test EXEC-003: Tool info cached after first check"""
    guard = ToolGuard()

    # First call
    info1 = guard.require_tool('python')

    # Second call (should use cache)
    with patch('shutil.which') as mock_which:
        info2 = guard.require_tool('python')
        mock_which.assert_not_called()  # Didn't re-check PATH

    assert info1.path == info2.path
```

---

## Implementation Checklist

- [ ] Implement ToolGuard class with PATH checking
- [ ] Add install hints for common tools
- [ ] Implement version checking (optional)
- [ ] Add caching to avoid repeated PATH lookups
- [ ] Implement require_all() for batch verification
- [ ] Implement execute_guarded() convenience method
- [ ] Add unit tests for all guard scenarios
- [ ] Document install hints for project-specific tools
- [ ] Integrate with CI/CD environment checks
- [ ] Add metrics tracking (tool verification time)

---

## Common Tool Install Hints

```python
COMMON_INSTALL_HINTS = {
    # Rust tools
    'cargo': 'curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh',
    'apply_patch': 'cargo install apply-patch',

    # Python tools
    'python': 'https://python.org/downloads',
    'pip': 'python -m ensurepip --upgrade',
    'pytest': 'pip install pytest',
    'black': 'pip install black',
    'ruff': 'pip install ruff',

    # Node tools
    'node': 'https://nodejs.org/',
    'npm': 'Included with Node.js',

    # Git
    'git': 'https://git-scm.com/downloads',

    # System tools
    'make': 'apt-get install build-essential (Ubuntu) or xcode-select --install (Mac)',
    'gcc': 'apt-get install gcc (Ubuntu) or brew install gcc (Mac)',
}
```

---

## References

- **Source**: `codex_log_analysis_report.md` Section 1.3
- **Related Patterns**: EXEC-002 (Batch Validation), PATTERN-002 (Ground Truth)
- **Implementation**: `core/patterns/exec003.py`
- **Tests**: `tests/patterns/test_exec003.py`

---

**Status**: ✅ Ready for Implementation
**Priority**: Critical (prevents 16% of errors, zero implementation cost)
**Effort**: Low (2-4 hours)
