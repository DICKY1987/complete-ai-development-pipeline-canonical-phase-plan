# Task Queue Directory

This directory contains the file-based task queue for phase execution.

## Structure

- queued/ - Phases waiting to execute
- unning/ - Phases currently executing
- complete/ - Successfully completed phases
- ailed/ - Failed phase executions

## Usage

Tasks are automatically managed by the orchestrator. Do not manually edit files in this directory.
