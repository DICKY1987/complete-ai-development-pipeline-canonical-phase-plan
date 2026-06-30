# Master Splinter - Multi-Agent Workstream Coordinator

This directory contains the Master Splinter system, a multi-agent workstream coordination tool for managing complex AI development workflows.

## Contents

### Core Python Modules
- `run_master_splinter.py` - Main entry point for running Master Splinter
- `multi_agent_workstream_coordinator.py` - Core coordination logic for multi-agent workflows
- `phase_plan_to_workstream.py` - Converts phase plans to workstreams
- `sync_workstreams_to_github.py` - Synchronizes workstreams with GitHub
- `validate_master_splinter_schema.py` - Schema validation for Master Splinter configurations

### Templates and Schemas
- `MASTER_SPLINTER_Phase_Plan_Template.yml` - YAML template for phase plans
- `MASTER_SPLINTER_Phase_Plan_Template.json` - JSON template for phase plans
- `MASTER_SPLINTER_PROCESS_STEPS_SCHEMA.yaml` - Schema defining valid process steps

### Documentation
- `PROCESS_DOCS_README.md` - Process documentation for Master Splinter

### Subdirectories
- `config/` - Configuration files for Master Splinter
- `plans/` - Phase plans and execution plans
- `workstreams/` - Active workstream definitions
- `safe_merge/` - Safe merge functionality
- `.claude/` - Claude AI integration files

## Purpose

Master Splinter coordinates multi-agent AI development workflows by:
- Breaking down complex tasks into manageable workstreams
- Coordinating multiple AI agents working in parallel
- Managing phase plans and execution strategies
- Synchronizing work with GitHub projects
- Ensuring safe merging of parallel work

## Usage

1. **Run Master Splinter**: Execute `run_master_splinter.py` to start the coordinator
2. **Create Phase Plans**: Use the provided templates to define phase plans
3. **Validate**: Run `validate_master_splinter_schema.py` to validate configurations
4. **Monitor**: Track workstream progress and coordination

## Architecture

Master Splinter uses a phase-based approach where:
1. Phase plans define high-level objectives
2. Workstreams break down phases into executable tasks
3. Multiple agents execute workstreams in parallel
4. Coordination ensures consistency and proper integration

## Integration

Master Splinter integrates with:
- GitHub Projects for task tracking
- Claude AI for intelligent assistance
- Safe merge system for conflict-free integration
- The broader AI development pipeline infrastructure
