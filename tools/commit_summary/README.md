# Commit Summary Generator

This directory contains tools for generating structured commit summaries.

## Contents

### `README_Commit Summary Generator  .md`
Documentation for the commit summary generator tool.

### `commit_summary.schema.json`
JSON schema defining the structure of commit summaries.

### `generate_commit_summary.ps1`
PowerShell script for automatically generating commit summaries.

## Purpose

This tool automates the creation of structured commit summaries, ensuring consistency and completeness in commit documentation. It helps maintain a clear history of changes by:
- Generating standardized commit messages
- Validating commit summary structure against schema
- Automating commit documentation workflow

## Usage

Run the `generate_commit_summary.ps1` script to generate a structured commit summary. The generated summary will conform to the schema defined in `commit_summary.schema.json`.
