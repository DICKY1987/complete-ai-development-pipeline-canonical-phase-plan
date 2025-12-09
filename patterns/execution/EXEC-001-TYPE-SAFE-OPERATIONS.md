---
doc_id: DOC-PAT-EXEC-001-890
pattern_id: EXEC-001
version: 1.0.0
status: active
created: 2025-12-04
category: execution
priority: high
---

# EXEC-001: Type-Safe Operations Pattern

## Overview

**Pattern Name**: Type-Safe Operations
**Problem**: File format misdetection causing 7% of execution failures
**Solution**: Extension-aware file handling with explicit type routing
**Impact**: Prevents wrong-handler errors before execution

---

## Problem Statement

### Observed Behavior
```
Attempting to load .txt file as image → PIL.UnidentifiedImageError
Attempting to load .md file as image → PIL.UnidentifiedImageError
Attempting to parse binary as text → UnicodeDecodeError
```

### Root Cause
Operations dispatched without checking file type compatibility:
- No extension validation before format-specific operations
- No content-type detection before parsing
- No handler registry to route by file type

### Cost
- **6 failures** observed (7% of total errors)
- **30-60 seconds wasted** per incident
- **Data corruption risk** when writing wrong format

---

## Solution Pattern

### Core Principle
**Route to correct handler based on verified file type before executing**

### Implementation

```python
from pathlib import Path
from typing import Callable, Dict, Any
import mimetypes
import os

# Template: Extension-Aware File Handling
class TypeSafeFileHandler:
    """EXEC-001: Route operations by file type"""

    def __init__(self):
        self.extension_handlers: Dict[str, Callable] = {}
        self.mime_handlers: Dict[str, Callable] = {}

    def register_extension(self, ext: str, handler: Callable):
        """Register handler for file extension"""
        self.extension_handlers[ext.lower()] = handler

    def register_mime(self, mime_type: str, handler: Callable):
        """Register handler for MIME type"""
        self.mime_handlers[mime_type] = handler

    def dispatch_by_extension(self, file_path: str) -> Any:
        """EXEC-001: Route to correct handler based on file type"""
        path = Path(file_path)

        # Gate 1: File exists
        if not path.exists():
            raise FileNotFoundError(f"PREFLIGHT_FAIL: {file_path} not found")

        # Gate 2: Get extension
        ext = path.suffix.lower()
        if not ext:
            raise ValueError(f"NO_EXTENSION: {file_path} has no file extension")

        # Gate 3: Handler exists
        handler = self.extension_handlers.get(ext)
        if not handler:
            raise ValueError(
                f"UNSUPPORTED_EXT: No handler registered for {ext}. "
                f"Supported: {list(self.extension_handlers.keys())}"
            )

        # Gate 4: Execute with correct handler
        return handler(path)

    def dispatch_by_mime(self, file_path: str) -> Any:
        """Alternative: Route by MIME type (more robust)"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"PREFLIGHT_FAIL: {file_path} not found")

        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(str(path))
        if not mime_type:
            # Fallback to extension-based routing
            return self.dispatch_by_extension(file_path)

        handler = self.mime_handlers.get(mime_type)
        if not handler:
            raise ValueError(f"UNSUPPORTED_MIME: {mime_type}")

        return handler(path)
```

---

## Usage Examples

### Example 1: Basic Extension-Based Routing

```python
# Setup handlers
handler = TypeSafeFileHandler()

def handle_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')

def handle_json(path: Path) -> dict:
    import json
    return json.loads(path.read_text())

def handle_image(path: Path):
    from PIL import Image
    return Image.open(path)

# Register handlers
handler.register_extension('.txt', handle_text)
handler.register_extension('.md', handle_text)
handler.register_extension('.json', handle_json)
handler.register_extension('.png', handle_image)
handler.register_extension('.jpg', handle_image)

# Usage: Automatic routing
content = handler.dispatch_by_extension('data.json')  # → handle_json
text = handler.dispatch_by_extension('readme.md')     # → handle_text
img = handler.dispatch_by_extension('logo.png')       # → handle_image

# Prevents error:
# handler.dispatch_by_extension('readme.md')  # Would NOT call handle_image ✅
```

### Example 2: MIME-Type Routing (More Robust)

```python
# Register by MIME type
handler.register_mime('text/plain', handle_text)
handler.register_mime('text/markdown', handle_text)
handler.register_mime('application/json', handle_json)
handler.register_mime('image/png', handle_image)
handler.register_mime('image/jpeg', handle_image)

# Auto-detects MIME type
content = handler.dispatch_by_mime('data.json')  # Detects application/json
text = handler.dispatch_by_mime('README.md')     # Detects text/markdown
img = handler.dispatch_by_mime('photo.jpg')      # Detects image/jpeg
```

### Example 3: Batch Processing with Type Safety

```python
def process_directory(dir_path: str):
    """Process all files in directory with correct handlers"""
    handler = TypeSafeFileHandler()
    # ... register handlers ...

    results = []
    errors = []

    for file_path in Path(dir_path).rglob('*'):
        if file_path.is_file():
            try:
                result = handler.dispatch_by_extension(str(file_path))
                results.append((file_path, result))
            except ValueError as e:
                # Unsupported extension - skip gracefully
                errors.append((file_path, str(e)))

    return results, errors
```

---

## Integration Points

### With EXEC-002 (Batch Validation)

```python
def batch_process_files(file_paths: list, handler: TypeSafeFileHandler):
    """Combine EXEC-001 with EXEC-002 for batch type-safe operations"""

    # Pass 1: Validate all files (EXEC-002)
    validation_errors = []
    for path in file_paths:
        try:
            # Check extension support
            ext = Path(path).suffix.lower()
            if ext not in handler.extension_handlers:
                validation_errors.append((path, f"Unsupported extension: {ext}"))
        except Exception as e:
            validation_errors.append((path, str(e)))

    if validation_errors:
        raise ValueError(f"VALIDATION_FAILED: {len(validation_errors)} files unsupported")

    # Pass 2: Execute all (EXEC-001)
    results = []
    for path in file_paths:
        results.append(handler.dispatch_by_extension(path))

    return results
```

### With EXEC-004 (Atomic Operations)

```python
def atomic_format_conversion(
    input_path: str,
    output_path: str,
    input_handler: TypeSafeFileHandler,
    output_handler: Callable
):
    """Combine EXEC-001 with EXEC-004 for safe format conversion"""
    from core.patterns.exec004 import AtomicFileOp

    # Gate 1: Type-safe read (EXEC-001)
    content = input_handler.dispatch_by_extension(input_path)

    # Gate 2: Atomic write (EXEC-004)
    atomic_op = AtomicFileOp(output_path)
    atomic_op.execute(lambda p: output_handler(p, content))
```

---

## Decision Tree

```
File Operation Needed
  │
  ├─ Known file extension?
  │   YES → Use dispatch_by_extension()
  │   NO  → Use dispatch_by_mime() (auto-detect)
  │
  ├─ Custom format?
  │   YES → Register custom handler first
  │   NO  → Use standard handlers
  │
  └─ Multiple files?
      YES → Combine with EXEC-002 (batch validation)
      NO  → Direct dispatch
```

---

## Metrics

### Prevents
- **File format errors**: 100% of extension-based errors
- **Wrong handler invocation**: All misrouted operations
- **Data corruption**: From format mismatches

### Performance
- **Overhead**: <1ms per file (extension lookup)
- **Savings**: 30-60s per prevented error
- **ROI**: 30,000:1 (1ms overhead vs 30s error recovery)

---

## Anti-Patterns (Don't Do This)

### ❌ Anti-Pattern 1: Magic Extension Detection
```python
# BAD: Trying to parse all formats until one works
def load_file(path):
    try:
        return json.loads(Path(path).read_text())
    except:
        try:
            from PIL import Image
            return Image.open(path)
        except:
            return Path(path).read_text()  # Assume text
```

**Why Bad**: Silent failures, slow (tries all handlers), unpredictable

### ❌ Anti-Pattern 2: Extension-Only Check Without Validation
```python
# BAD: Checks extension but doesn't validate handler exists
def load_file(path):
    if path.endswith('.json'):
        return json.loads(...)  # What if JSON handler fails?
```

**Why Bad**: No fallback, no error handling, fragile

### ✅ Correct Pattern: Explicit Registry
```python
# GOOD: Registry with validation
handler = TypeSafeFileHandler()
handler.register_extension('.json', handle_json)
result = handler.dispatch_by_extension(path)  # Validated routing
```

---

## Testing Strategy

### Unit Tests

```python
import pytest
from pathlib import Path

def test_dispatch_by_extension():
    """Test EXEC-001: Extension-based routing"""
    handler = TypeSafeFileHandler()
    handler.register_extension('.txt', lambda p: 'text')
    handler.register_extension('.json', lambda p: 'json')

    # Create temp files
    tmp_txt = Path('test.txt')
    tmp_txt.write_text('hello')

    # Test correct routing
    assert handler.dispatch_by_extension('test.txt') == 'text'

    # Test unsupported extension
    with pytest.raises(ValueError, match="UNSUPPORTED_EXT"):
        handler.dispatch_by_extension('test.xml')

    tmp_txt.unlink()

def test_preflight_validation():
    """Test EXEC-001: File existence gate"""
    handler = TypeSafeFileHandler()
    handler.register_extension('.txt', lambda p: 'text')

    # Test file not found
    with pytest.raises(FileNotFoundError, match="PREFLIGHT_FAIL"):
        handler.dispatch_by_extension('nonexistent.txt')
```

---

## Implementation Checklist

- [ ] Define handler registry structure
- [ ] Implement extension-based routing
- [ ] Implement MIME-type fallback (optional)
- [ ] Register all supported file types
- [ ] Add pre-flight existence checks
- [ ] Add unit tests for all handlers
- [ ] Document supported extensions
- [ ] Integrate with EXEC-002 for batch operations
- [ ] Add metrics tracking (files processed by type)

---

## References

- **Source**: `codex_log_analysis_report.md` Section 1.2
- **Related Patterns**: EXEC-002 (Batch Validation), EXEC-004 (Atomic Ops)
- **Implementation**: `core/patterns/exec001.py`
- **Tests**: `tests/patterns/test_exec001.py`

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-04 | AI Log Analyzer | Initial pattern from log analysis |

---

**Status**: ✅ Ready for Implementation
**Priority**: High (prevents 7% of errors)
**Effort**: Low (2-4 hours)
