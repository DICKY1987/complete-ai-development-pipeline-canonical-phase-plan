"""
Orchestrator package for job management and execution.

The orchestrator is the central coordinator that:
- Manages job lifecycle (queued → running → completed/failed)
- Dispatches jobs to appropriate adapters
- Updates state store with results
- Handles retries and escalations
"""
DOC_ID: DOC-PAT-ORCHESTRATOR-INIT-450

__version__ = "0.1.0"
