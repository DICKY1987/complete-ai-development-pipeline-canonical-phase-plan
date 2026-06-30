# Data Directory

This directory contains data files used by the AI development pipeline system.

## Contents

### `docs_inventory.jsonl`
JSONL file containing an inventory of all documentation in the project. Used for documentation discovery and management.

### `pipeline_errors.jsonl`
JSONL file containing pipeline error logs and records. Used for error tracking and debugging.

## Purpose

This directory centralizes all data files that are generated or consumed by the pipeline tools and scripts. It provides a single location for:
- Documentation inventories
- Error logs and tracking data
- Other structured data outputs from pipeline operations

## Usage

These files are typically read and written by various scripts in the `/scripts` and `/tools` directories. They should not be manually edited unless you understand their schema and purpose.
