# Path Standardizer Plugin

Uses CCPM's path validation tools to ensure consistent path usage across the codebase.

## Features

- Validates path conventions (forward slashes, absolute vs relative)
- Auto-fixes common path issues
- Cross-platform compatibility (Windows/Unix)

## Usage

```bash
# Validate paths
python src/plugins/path_standardizer/plugin.py file1.py file2.py

# Validate and fix
python src/plugins/path_standardizer/plugin.py file1.py file2.py --fix
```

## Integration

Add to pipeline at state: `S0_MECHANICAL_AUTOFIX` (runs before other plugins)

## Configuration

None required - uses scripts/check-path-standards.sh and scripts/fix-path-standards.sh

