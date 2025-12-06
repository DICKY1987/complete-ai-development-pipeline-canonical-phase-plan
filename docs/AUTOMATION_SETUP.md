# Automation Setup Guide

## Overview

This document describes the automation infrastructure for MASTER_SPLINTER.

## Components

### 1. CI/CD Pipeline
- **Location**: `.github/workflows/ci.yml`
- **Triggers**: Push to main/develop/feature branches, Pull requests
- **Actions**: Lint, type check, test, validate configs

### 2. Scheduled Orchestrator
- **Location**: `.github/workflows/scheduled-orchestrator.yml`
- **Schedule**: Daily at 2 AM UTC
- **Actions**: Run master orchestrator, upload reports, ping healthcheck

### 3. Pre-commit Hooks
- **Location**: `.pre-commit-config.yaml`
- **Hooks**: YAML/JSON validation, ruff, mypy, file cleanup
- **Install**: `pre-commit install`

### 4. CLI Adapter
- **Location**: `core/cli_adapter.py`
- **Purpose**: Centralized subprocess execution with retry logic
- **Usage**: `from core import CLIAdapter`

### 5. Config Validator
- **Location**: `scripts/validate_config.py`
- **Purpose**: Validate tool_profiles.json against JSON Schema
- **Usage**: `python scripts/validate_config.py`

### 6. Monitoring
- **Location**: `scripts/setup_monitoring.py`
- **Integration**: healthchecks.io
- **Setup**: Add HEALTHCHECK_URL to environment/secrets

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Install pre-commit hooks: `pre-commit install`
3. Run tests: `pytest tests/`
4. Validate configs: `python scripts/validate_config.py`

## Configuration

- Tool profiles: `config/tool_profiles.json`
- Circuit breakers: `config/circuit_breakers.yaml`
- Environment: Set `HEALTHCHECK_URL` for monitoring

## Maintenance

- Pre-commit hooks run automatically on commit
- CI pipeline runs on every push/PR
- Scheduled orchestrator runs daily
- Review reports in `reports/` directory
