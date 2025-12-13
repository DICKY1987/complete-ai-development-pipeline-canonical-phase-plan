# Source Code Directory

This directory contains source code modules and libraries for the AI development pipeline system.

## Contents

### `path_registry.py`
Path registry module for managing and resolving file paths across the system.

### `uet_framework/`
Universal Execution Templates (UET) Framework - A Python module providing:
- AIM (Autonomous Intelligence Management) integration
- Bridge functionality for connecting components
- Pool interface for resource management

## Purpose

The `src/` directory serves as the main location for:
- Core Python modules and libraries
- Reusable components and frameworks
- Shared utilities and helpers

This is the primary source code location for the project's Python implementation.

## Structure

- Top-level modules: Utility modules used across the system
- Subdirectories: Framework and subsystem implementations

## Usage

Import modules from this directory in your Python code:

```python
from src.path_registry import PathRegistry
from src.uet_framework.aim import bridge
```

Make sure the project root is in your Python path to import from `src/`.
