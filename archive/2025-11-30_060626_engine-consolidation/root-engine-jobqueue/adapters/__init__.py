"""
Tool adapters for the engine.

Each adapter wraps a specific CLI tool and implements AdapterInterface.
Adapters are responsible for:
- Building correct command lines from job specifications
- Executing tools in pseudo-terminals
- Capturing logs and results
- Returning standardized JobResult objects
"""
DOC_ID: DOC-PAT-ADAPTERS-INIT-444

__version__ = "0.1.0"
