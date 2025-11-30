"""
Protocol interfaces for engine components.

These protocols define the contracts between different sections
of the pipeline without requiring tight coupling or inheritance.
"""
# DOC_ID: DOC-PAT-INTERFACES-INIT-448

from engine.interfaces.state_interface import StateInterface
from engine.interfaces.adapter_interface import AdapterInterface
from engine.interfaces.orchestrator_interface import OrchestratorInterface

__all__ = [
    "StateInterface",
    "AdapterInterface",
    "OrchestratorInterface",
]
