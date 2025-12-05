# PAT-FILE-SCOPE-ENFORCE-001: File Scope Enforcement

## Purpose
Ensure all file operations respect declared file_scope boundaries.

## Implementation
1. Before any file write or modify operation, check against:
   - `file_scope.modify` for allowed modification paths
   - `file_scope.create` for allowed creation paths
   - `forbidden_paths` that must never be touched
2. Use glob pattern matching to validate paths.
3. Reject operations that violate scope with a clear error message.

## Validation
```python
def validate_file_scope(filepath, file_scope):
    import fnmatch

    for pattern in file_scope["forbidden_paths"]:
        if fnmatch.fnmatch(filepath, pattern):
            raise ScopeViolationError(f"{filepath} matches forbidden pattern {pattern}")

    for pattern in file_scope["modify"] + file_scope["create"]:
        if fnmatch.fnmatch(filepath, pattern):
            return True

    raise ScopeViolationError(f"{filepath} not in allowed scope")
```

## Success Criteria
- No files modified outside declared scope.
- All scope violations logged and blocked.
