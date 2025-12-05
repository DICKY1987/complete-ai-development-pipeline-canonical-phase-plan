# Shared GitHub Client

**Status**: Active (migrated 2025-12-05)

## Purpose

Unified GitHub API client for all GitHub integration scripts in this repository.

## Usage

```python
from .github.shared.github_client import GitHubProjectClient

client = GitHubProjectClient()
# Use client for GitHub Projects v2 operations
```

## Migration

This module consolidates duplicate GitHub API clients from:
- `.github/scripts/github_project_utils.py` (mature implementation)
- `.github/github_integration_v2/executors/phase_sync.py` (inline GraphQL)

All scripts now import from this shared location.

## Features

- ✅ GitHub Projects v2 GraphQL support
- ✅ REST API support with retries
- ✅ Automatic token handling (PROJECT_TOKEN or GITHUB_TOKEN)
- ✅ Circuit breaker for rate limits
- ✅ Project/milestone/item management

## Dependencies

- `requests` - HTTP client
- Python 3.11+

---

**Last Updated**: 2025-12-05
