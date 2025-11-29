---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-EXAMPLE_SIMPLE_TASK-013
---

# Example 01: Simple Task - Hello World

**Pattern**: Single-step workstream  
**Complexity**: Beginner  
**Estimated Duration**: 2-5 minutes  
**Tool**: Aider (AI coding assistant)

---

## Purpose

This example demonstrates the **simplest possible workstream**: creating a single Python file with basic functionality. Use this pattern when you need to:

- Create a new module or file
- Make a simple, isolated code change
- Add a single feature to an existing file
- Perform basic refactoring

---

## What This Example Demonstrates

✅ **Core Workstream Structure**
- Minimal required fields
- Basic metadata and configuration
- File scope and ownership

✅ **Tool Integration**
- Using Aider as the execution tool
- Task specification for AI guidance
- Acceptance test validation

✅ **Error Handling**
- Circuit breaker configuration
- Retry logic (max 3 attempts)
- Error repeat detection

---

## Workstream File Breakdown

### File Location

```
workstreams/examples/01_simple_task.json
```

### Key Components

#### 1. Identification
```json
{
  "id": "ws-example-01-simple-task",
  "openspec_change": "EX-001",
  "ccpm_issue": 1001
}
```

**Why**: Unique ID prevents conflicts, links to requirements and issues for traceability.

---

#### 2. File Ownership
```json
{
  "files_scope": ["examples/hello_world.py"],
  "files_create": ["examples/hello_world.py"]
}
```

**Why**: 
- `files_scope` claims ownership to prevent conflicts with other workstreams
- `files_create` explicitly allows file creation
- Both must match for new files

---

#### 3. Task Specification
```json
{
  "tasks": [
    "Create a simple hello world Python module",
    "Add docstring explaining the module purpose",
    "Include basic error handling"
  ]
}
```

**Why**: Clear, actionable instructions guide the AI tool. Each task is:
- Concrete and specific
- Independently verifiable
- Focused on a single concern

---

#### 4. Acceptance Tests
```json
{
  "acceptance_tests": [
    "python -c \"import examples.hello_world; print('Import OK')\"",
    "python examples/hello_world.py"
  ]
}
```

**Why**: 
- First test: Validates module can be imported (no syntax errors)
- Second test: Validates module can be executed directly
- Both must pass for workstream to succeed

---

#### 5. Circuit Breaker
```json
{
  "circuit_breaker": {
    "max_attempts": 3,
    "max_error_repeats": 2
  }
}
```

**Why**:
- `max_attempts`: Prevents infinite retry loops (fail after 3 tries)
- `max_error_repeats`: Detects stuck states (escalate if same error 2x)
- Safety mechanism for production use

---

## How to Execute

### Prerequisites

1. **Python environment** with pipeline installed:
   ```bash
   python -m pip install -r requirements.txt
   ```

2. **Aider installed** (if using Aider tool):
   ```bash
   pip install aider-chat
   ```

3. **Environment variables** (if needed):
   ```bash
   export OPENAI_API_KEY=your_api_key  # For Aider with OpenAI
   # OR
   export ANTHROPIC_API_KEY=your_api_key  # For Aider with Claude
   ```

---

### Execution Methods

#### Method 1: Using Pipeline Script (Recommended)

```bash
# From repository root
python scripts/run_workstream.py --ws-id ws-example-01-simple-task
```

**Expected Output**:
```
✓ Loading workstream: ws-example-01-simple-task
✓ Validating schema
✓ Checking file scope conflicts
✓ Initializing Aider tool
✓ Executing tasks (1/1)
  → Creating examples/hello_world.py
✓ Running acceptance tests (2/2)
  → Import test: PASS
  → Execution test: PASS
✓ Workstream complete in 2m 34s
```

---

#### Method 2: Manual Validation

```bash
# Validate workstream structure
python scripts/validate_workstreams.py workstreams/examples/01_simple_task.json

# Expected: "✓ Schema valid, 0 errors"
```

---

#### Method 3: Direct Tool Execution

```bash
# If you want to see raw Aider interaction
aider --message "Create a simple hello world Python module in examples/hello_world.py with docstring and error handling"
```

---

## Expected Results

### Created File: `examples/hello_world.py`

```python
"""
Hello World Module

A simple example module demonstrating basic Python structure.
"""

import sys


def hello(name: str = "World") -> str:
    """
    Return a greeting message.
    
    Args:
        name: Name to greet (default: "World")
        
    Returns:
        Greeting string
    """
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    
    return f"Hello, {name}!"


def main() -> int:
    """Main entry point."""
    try:
        message = hello()
        print(message)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

---

### Acceptance Test Output

**Test 1: Import Check**
```bash
$ python -c "import examples.hello_world; print('Import OK')"
Import OK
```

**Test 2: Execution Check**
```bash
$ python examples/hello_world.py
Hello, World!
```

---

## Troubleshooting

### Issue: "Workstream ID already exists"

**Cause**: Another workstream with same ID in database  
**Fix**: 
```bash
# Check existing workstreams
python scripts/list_workstreams.py

# Use different ID or clean up database
```

---

### Issue: "File scope conflict"

**Cause**: Another workstream claims ownership of `examples/hello_world.py`  
**Fix**:
```bash
# Check file ownership
python scripts/check_file_scope.py examples/hello_world.py

# Wait for other workstream to complete or change file path
```

---

### Issue: "Aider not found"

**Cause**: Aider tool not installed  
**Fix**:
```bash
pip install aider-chat

# Verify installation
aider --version
```

---

### Issue: "Acceptance tests failed"

**Cause**: Generated code doesn't meet requirements  
**Fix**:
1. Check circuit breaker logs for errors
2. Review generated file manually
3. Adjust tasks to be more specific
4. Increase max_attempts if needed

---

## Customization Examples

### Change Output Location

```json
{
  "files_scope": ["src/utils/hello.py"],
  "files_create": ["src/utils/hello.py"]
}
```

---

### Add More Tasks

```json
{
  "tasks": [
    "Create a simple hello world Python module",
    "Add docstring explaining the module purpose",
    "Include basic error handling",
    "Add type hints to all functions",
    "Include unit tests in the same file"
  ]
}
```

---

### Use Different Tool

```json
{
  "tool": "codex",
  "_comment": "Use OpenAI Codex instead of Aider"
}
```

---

### Adjust Circuit Breaker

```json
{
  "circuit_breaker": {
    "max_attempts": 5,
    "max_error_repeats": 3
  },
  "_comment": "More lenient for complex tasks"
}
```

---

## Learning Points

### ✅ Best Practices Demonstrated

1. **Clear task specification** - Each task is actionable and specific
2. **Comprehensive tests** - Both import and execution validated
3. **Error boundaries** - Circuit breaker prevents runaway execution
4. **File ownership** - Explicit scope prevents conflicts
5. **Metadata tracking** - Owner, priority, duration for reporting

---

### ⚠️ Common Pitfalls to Avoid

1. **Vague tasks** - "Make it better" → Too ambiguous for AI
2. **Missing tests** - No validation means no confidence
3. **Overlapping scope** - Multiple workstreams editing same file
4. **No circuit breaker** - Infinite retries waste resources
5. **Wrong tool** - Complex tasks need more capable models

---

## Next Steps

After mastering simple tasks, explore:

- **Example 02**: Parallel Execution - Multiple tasks in parallel
- **Example 03**: Error Handling - Intentional failures and recovery
- **Example 04**: Multi-Phase - Complex workflows with checkpoints
- **Example 05**: SAGA Pattern - Rollback and compensation

---

## Related Documentation

- [Workstream Authoring Guide](../workstream_authoring_guide.md)
- [Tool Profile Configuration](../../config/examples/tool_profile_annotated.yaml)
- [Circuit Breaker Documentation](../ARCHITECTURE.md#circuit-breakers)
- [Acceptance Testing Best Practices](../plugin-quick-reference.md)

---

## Validation Checklist

Before using this pattern in production:

- [ ] Workstream validates with `validate_workstreams.py`
- [ ] File scope doesn't conflict with existing workstreams
- [ ] Tool profile exists and is configured
- [ ] Acceptance tests cover all requirements
- [ ] Circuit breaker values are appropriate
- [ ] Metadata is complete (owner, priority, duration)

---

**Last Updated**: 2025-11-22  
**Difficulty**: ⭐ Beginner  
**Execution Time**: 2-5 minutes  
**Success Rate**: ~95% (simple tasks rarely fail)
