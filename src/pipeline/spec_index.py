"""
Spec Index Mapping Logic for AI Development Pipeline.

Provides intelligent mapping from spec IDX tags to code modules, functions,
phases, and versions based on semantic analysis of tag structure and context.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# IDX tag pattern: [IDX-CATEGORY-SUBCATEGORY-NUMBER]
IDX_PATTERN = re.compile(r"\[IDX-([A-Z]+)-([A-Z0-9\-]+)-(\d+)\]")


@dataclass
class SpecMapping:
    """
    Mapping from a spec IDX tag to implementation details.

    Attributes:
        idx: The IDX tag (e.g., "IDX-DB-SCHEMA-01")
        description: Description from the spec (line content or nearest heading)
        source_file: Relative path to spec file containing the IDX tag
        line: Line number in source file
        module: Target Python module (e.g., "src/pipeline/db.py")
        function_or_class: Suggested function/class name (e.g., "init_db")
        phase: Implementation phase (PH-01, PH-02, PH-03, etc.)
        version: Version tag (v1.0, v2.0, etc.)
    """
    idx: str
    description: str
    source_file: str
    line: int
    module: str
    function_or_class: str
    phase: str
    version: str

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary."""
        return asdict(self)


def parse_idx_tag(idx: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """
    Parse IDX tag into components.

    Args:
        idx: IDX tag string (e.g., "IDX-DB-SCHEMA-01")

    Returns:
        Tuple of (category, subcategory, number) or (None, None, None) if invalid

    Examples:
        >>> parse_idx_tag("IDX-DB-SCHEMA-01")
        ("DB", "SCHEMA", 1)
        >>> parse_idx_tag("IDX-PROMPT-AIDER-CONFIG-05")
        ("PROMPT", "AIDER-CONFIG", 5)
    """
    # Remove brackets if present
    idx_clean = idx.strip("[]")

    match = IDX_PATTERN.match(f"[{idx_clean}]")
    if not match:
        return None, None, None

    category = match.group(1)
    subcategory = match.group(2)
    number = int(match.group(3))

    return category, subcategory, number


def infer_module(category: str, subcategory: str) -> str:
    """
    Infer target module from IDX category and subcategory.

    Semantic Rules:
    - DB → src/pipeline/db.py (database operations)
    - PROMPT → src/pipeline/prompts.py (AI prompts)
    - TOOL → src/pipeline/tools.py (external tool adapters)
    - WORKTREE → src/pipeline/worktree.py (git worktree management)
    - BUNDLE → src/pipeline/bundles.py (workstream bundles)
    - CB (circuit breaker) → src/pipeline/circuit_breakers.py
    - RECOVERY → src/pipeline/recovery.py
    - ORCHESTRATOR → src/pipeline/orchestrator.py
    - SCHEDULER → src/pipeline/scheduler.py
    - EXECUTOR → src/pipeline/executor.py
    - STATE → src/pipeline/db.py (state machine in DB module)
    - SCHEMA → schema/schema.sql (database schema)
    - CONFIG → config/ directory
    - DOC → docs/ directory

    Args:
        category: IDX category (e.g., "DB", "PROMPT")
        subcategory: IDX subcategory (e.g., "SCHEMA", "CRUD")

    Returns:
        Module path string
    """
    # Mapping rules based on category
    module_map = {
        "DB": "src/pipeline/db.py",
        "DATABASE": "src/pipeline/db.py",
        "STATE": "src/pipeline/db.py",
        "PROMPT": "src/pipeline/prompts.py",
        "TOOL": "src/pipeline/tools.py",
        "ADAPTER": "src/pipeline/tools.py",
        "WORKTREE": "src/pipeline/worktree.py",
        "BUNDLE": "src/pipeline/bundles.py",
        "CB": "src/pipeline/circuit_breakers.py",
        "CIRCUIT": "src/pipeline/circuit_breakers.py",
        "RECOVERY": "src/pipeline/recovery.py",
        "ORCHESTRATOR": "src/pipeline/orchestrator.py",
        "SCHEDULER": "src/pipeline/scheduler.py",
        "EXECUTOR": "src/pipeline/executor.py",
        "SCHEMA": "schema/schema.sql",
        "CONFIG": "config/",
        "DOC": "docs/",
        "DOCS": "docs/",
    }

    module = module_map.get(category, "src/pipeline/")

    # Subcategory refinements
    if subcategory == "SCHEMA":
        return "schema/schema.sql"
    elif subcategory.startswith("TEST"):
        return f"tests/pipeline/test_{category.lower()}.py"
    elif subcategory.startswith("SCRIPT"):
        return "scripts/"

    return module


def infer_function_or_class(category: str, subcategory: str, description: str) -> str:
    """
    Infer function or class name from IDX components and description.

    Semantic Rules:
    - SCHEMA → table name or init_schema()
    - CRUD → create_*, update_*, delete_*, get_* operations
    - CONNECTION → get_connection(), init_db()
    - STATE → validate_state_transition(), update_*_status()
    - PROMPT → render_prompt(), get_prompt_template()
    - TOOL → run_tool(), get_tool_profile()
    - WORKTREE → create_worktree(), cleanup_worktree()

    Args:
        category: IDX category
        subcategory: IDX subcategory
        description: Description text from spec

    Returns:
        Function or class name suggestion
    """
    # Common patterns
    if "create" in description.lower():
        return "create_" + subcategory.lower().replace("-", "_")
    elif "update" in description.lower():
        return "update_" + subcategory.lower().replace("-", "_")
    elif "delete" in description.lower() or "remove" in description.lower():
        return "delete_" + subcategory.lower().replace("-", "_")
    elif "get" in description.lower() or "fetch" in description.lower():
        return "get_" + subcategory.lower().replace("-", "_")
    elif "validate" in description.lower():
        return "validate_" + subcategory.lower().replace("-", "_")
    elif "init" in description.lower():
        return "init_" + subcategory.lower().replace("-", "_")
    elif "run" in description.lower() or "execute" in description.lower():
        return "run_" + subcategory.lower().replace("-", "_")

    # Category-specific defaults
    category_defaults = {
        "DB": "db_" + subcategory.lower().replace("-", "_"),
        "PROMPT": "render_" + subcategory.lower().replace("-", "_"),
        "TOOL": "run_" + subcategory.lower().replace("-", "_"),
        "WORKTREE": "manage_" + subcategory.lower().replace("-", "_"),
        "STATE": "validate_" + subcategory.lower().replace("-", "_"),
        "SCHEMA": subcategory.lower().replace("-", "_") + "_table",
    }

    return category_defaults.get(category, subcategory.lower().replace("-", "_"))


def infer_phase(category: str, subcategory: str) -> str:
    """
    Infer implementation phase from IDX category and subcategory.

    Phase Rules:
    - PH-01: Spec mapping, index scanning, module stubs
    - PH-02: Database, state machine, CRUD
    - PH-03: Tool adapters, profiles, integration
    - PH-04: Orchestration, scheduling, execution
    - PH-05: Circuit breakers, recovery, observability
    - PH-06: Bundles, worktrees, full pipeline

    Args:
        category: IDX category
        subcategory: IDX subcategory

    Returns:
        Phase identifier (e.g., "PH-02")
    """
    # Phase assignment based on category
    phase_map = {
        "SPEC": "PH-01",
        "INDEX": "PH-01",
        "STUB": "PH-01",
        "DB": "PH-02",
        "DATABASE": "PH-02",
        "STATE": "PH-02",
        "SCHEMA": "PH-02",
        "CRUD": "PH-02",
        "TOOL": "PH-03",
        "ADAPTER": "PH-03",
        "PROMPT": "PH-03",
        "PROFILE": "PH-03",
        "ORCHESTRATOR": "PH-04",
        "SCHEDULER": "PH-04",
        "EXECUTOR": "PH-04",
        "CB": "PH-05",
        "CIRCUIT": "PH-05",
        "RECOVERY": "PH-05",
        "BUNDLE": "PH-06",
        "WORKTREE": "PH-06",
    }

    return phase_map.get(category, "TBD")


def infer_version(category: str, number: int) -> str:
    """
    Infer version from IDX category and number.

    Version Rules:
    - v1.0: Core functionality (numbers 01-50)
    - v2.0: Enhanced features (numbers 51-99)
    - v3.0: Advanced features (numbers 100+)

    Args:
        category: IDX category
        number: IDX number component

    Returns:
        Version string (e.g., "v1.0")
    """
    if number <= 50:
        return "v1.0"
    elif number <= 99:
        return "v2.0"
    else:
        return "v3.0"


def create_mapping(
    idx: str,
    description: str,
    source_file: str,
    line: int
) -> SpecMapping:
    """
    Create intelligent spec mapping from IDX tag.

    Applies semantic rules to infer module, function, phase, and version.

    Args:
        idx: IDX tag (e.g., "IDX-DB-SCHEMA-01")
        description: Description from spec
        source_file: Path to spec file
        line: Line number

    Returns:
        SpecMapping with inferred implementation details
    """
    category, subcategory, number = parse_idx_tag(idx)

    if category is None:
        # Fallback for unparseable IDX
        return SpecMapping(
            idx=idx,
            description=description,
            source_file=source_file,
            line=line,
            module="TBD",
            function_or_class="TBD",
            phase="TBD",
            version="v1.0"
        )

    return SpecMapping(
        idx=idx,
        description=description,
        source_file=source_file,
        line=line,
        module=infer_module(category, subcategory),
        function_or_class=infer_function_or_class(category, subcategory, description),
        phase=infer_phase(category, subcategory),
        version=infer_version(category, number)
    )


def generate_mapping_table(mappings: List[SpecMapping]) -> str:
    """
    Generate Markdown table from spec mappings.

    Args:
        mappings: List of SpecMapping objects

    Returns:
        Formatted Markdown table string
    """
    if not mappings:
        return "_No IDX tags found in specification documents._\n"

    # Table header
    table = "| IDX | Description | Source File | Line | Module | Function/Class | Phase | Version |\n"
    table += "|-----|-------------|-------------|------|--------|----------------|-------|----------|\n"

    # Table rows
    for m in mappings:
        # Truncate long descriptions
        desc = m.description[:50] + "..." if len(m.description) > 50 else m.description
        table += f"| {m.idx} | {desc} | {m.source_file} | {m.line} | {m.module} | {m.function_or_class} | {m.phase} | {m.version} |\n"

    return table
