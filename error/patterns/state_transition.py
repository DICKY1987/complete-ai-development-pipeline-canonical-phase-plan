"""State Transition Gap Analysis.

Creates state diagrams and identifies missing state transitions.
Most bugs are illegal state transitions that aren't handled.

Pattern: What transitions are missing?
1. List all valid states
2. List all state transitions implemented
3. Generate matrix of ALL possible transitions
4. Gap = (All Possible) - (Implemented)
"""
# DOC_ID: DOC-ERROR-PATTERNS-STATE-TRANSITION-053
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .types import (
    PatternCategory,
    PatternFinding,
    PatternSeverity,
    StateDiagram,
    StateTransition,
)


def extract_state_machine(file_path: Path) -> Optional[StateDiagram]:
    """Extract state machine definition from a Python file.
    
    Looks for patterns like:
    - State constants (S_INIT, STATE_*, etc.)
    - State transition functions
    - Current state tracking
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        StateDiagram if state machine patterns found, None otherwise
    """
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return None
    
    states: Set[str] = set()
    transitions: List[StateTransition] = []
    initial_state: Optional[str] = None
    terminal_states: Set[str] = set()
    
    # Find state constants
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    # Pattern: S_*, STATE_*, *_STATE
                    if re.match(r"^S_[A-Z_]+$", name) or re.match(r"^STATE_[A-Z_]+$", name):
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                            states.add(node.value.value)
                            # Detect initial/terminal states
                            if "INIT" in name or "START" in name:
                                initial_state = node.value.value
                            if "SUCCESS" in name or "DONE" in name or "END" in name or "FINAL" in name:
                                terminal_states.add(node.value.value)
                            if "QUARANTINE" in name or "ERROR" in name or "FAIL" in name:
                                terminal_states.add(node.value.value)
    
    # Find state transition patterns
    transitions = _extract_transitions(tree, states)
    
    if not states:
        return None
    
    return StateDiagram(
        name=file_path.stem,
        states=states,
        transitions=transitions,
        initial_state=initial_state,
        terminal_states=terminal_states,
    )


def _extract_transitions(tree: ast.Module, known_states: Set[str]) -> List[StateTransition]:
    """Extract state transitions from AST.
    
    Looks for patterns like:
    - ctx.current_state = S_NEW_STATE
    - if current_state == S_OLD_STATE: current_state = S_NEW_STATE
    """
    transitions: List[StateTransition] = []
    seen: Set[Tuple[str, str]] = set()
    
    class TransitionVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_from_state: Optional[str] = None
        
        def visit_If(self, node: ast.If):
            # Check for state comparison in condition
            from_state = self._extract_state_from_condition(node.test)
            if from_state:
                old_from = self.current_from_state
                self.current_from_state = from_state
                self.generic_visit(node)
                self.current_from_state = old_from
            else:
                self.generic_visit(node)
        
        def visit_Assign(self, node: ast.Assign):
            # Check for state assignment
            for target in node.targets:
                if self._is_state_variable(target):
                    to_state = self._extract_state_value(node.value)
                    if to_state and to_state in known_states:
                        from_state = self.current_from_state or "UNKNOWN"
                        key = (from_state, to_state)
                        if key not in seen:
                            seen.add(key)
                            transitions.append(StateTransition(
                                from_state=from_state,
                                to_state=to_state,
                                trigger="code_assignment",
                                is_implemented=True,
                                is_valid=True,
                            ))
            self.generic_visit(node)
        
        def _is_state_variable(self, node: ast.expr) -> bool:
            """Check if a node is a state variable reference."""
            if isinstance(node, ast.Attribute):
                return node.attr in ("current_state", "state", "_state")
            if isinstance(node, ast.Name):
                return node.id in ("current_state", "state", "_state")
            return False
        
        def _extract_state_from_condition(self, node: ast.expr) -> Optional[str]:
            """Extract state value from a comparison condition."""
            if isinstance(node, ast.Compare):
                left = node.left
                if self._is_state_variable(left):
                    for comparator in node.comparators:
                        val = self._extract_state_value(comparator)
                        if val and val in known_states:
                            return val
            if isinstance(node, ast.BoolOp):
                for value in node.values:
                    result = self._extract_state_from_condition(value)
                    if result:
                        return result
            return None
        
        def _extract_state_value(self, node: ast.expr) -> Optional[str]:
            """Extract a state constant value from an AST node."""
            if isinstance(node, ast.Constant):
                return str(node.value) if isinstance(node.value, str) else None
            if isinstance(node, ast.Name):
                # Reference to a state constant
                return node.id
            return None
    
    visitor = TransitionVisitor()
    visitor.visit(tree)
    
    return transitions


def analyze_state_gaps(diagram: StateDiagram) -> List[PatternFinding]:
    """Analyze a state diagram for missing transitions.
    
    Args:
        diagram: The state diagram to analyze
        
    Returns:
        List of findings about missing state handling
    """
    findings: List[PatternFinding] = []
    
    # Get missing transitions
    missing = diagram.get_missing_transitions()
    
    # Filter to only potentially valid missing transitions
    # (e.g., don't report missing transitions from terminal states)
    for transition in missing:
        # Skip transitions from terminal states
        if transition.from_state in diagram.terminal_states:
            continue
        
        # Skip self-transitions (usually intentional)
        if transition.from_state == transition.to_state:
            continue
        
        severity = PatternSeverity.MINOR
        # Higher severity if transitioning to error state isn't handled
        if any(s in transition.to_state.upper() for s in ["ERROR", "FAIL", "QUARANTINE"]):
            severity = PatternSeverity.MAJOR
        
        findings.append(PatternFinding(
            pattern_category=PatternCategory.STATE_TRANSITION,
            severity=severity,
            file_path="",  # Will be set by caller
            code="STG-001",
            message=f"Missing state transition: {transition.from_state} → {transition.to_state}",
            suggested_fix=f"Add handler for transition from {transition.from_state} to {transition.to_state}",
            context={
                "from_state": transition.from_state,
                "to_state": transition.to_state,
                "diagram_name": diagram.name,
            },
        ))
    
    # Check for unreachable states
    reachable = _find_reachable_states(diagram)
    unreachable = diagram.states - reachable - {diagram.initial_state}
    
    for state in unreachable:
        findings.append(PatternFinding(
            pattern_category=PatternCategory.STATE_TRANSITION,
            severity=PatternSeverity.MAJOR,
            file_path="",
            code="STG-002",
            message=f"Unreachable state: {state}",
            suggested_fix=f"Add transition path to reach state {state} or remove it",
            context={"state": state, "diagram_name": diagram.name},
        ))
    
    # Check for dead-end states (non-terminal with no outgoing)
    for state in diagram.states:
        if state in diagram.terminal_states:
            continue
        outgoing = [t for t in diagram.transitions if t.from_state == state]
        if not outgoing and state != diagram.initial_state:
            findings.append(PatternFinding(
                pattern_category=PatternCategory.STATE_TRANSITION,
                severity=PatternSeverity.MAJOR,
                file_path="",
                code="STG-003",
                message=f"Dead-end state (no outgoing transitions): {state}",
                suggested_fix=f"Add outgoing transitions from {state} or mark as terminal",
                context={"state": state, "diagram_name": diagram.name},
            ))
    
    return findings


def _find_reachable_states(diagram: StateDiagram) -> Set[str]:
    """Find all states reachable from the initial state."""
    if not diagram.initial_state:
        return diagram.states  # If no initial, assume all reachable
    
    reachable: Set[str] = {diagram.initial_state}
    frontier = [diagram.initial_state]
    
    while frontier:
        current = frontier.pop()
        for transition in diagram.transitions:
            if transition.from_state == current and transition.to_state not in reachable:
                reachable.add(transition.to_state)
                frontier.append(transition.to_state)
    
    return reachable


def generate_transition_matrix(diagram: StateDiagram) -> Dict[str, Dict[str, bool]]:
    """Generate a transition matrix showing implemented vs missing.
    
    Args:
        diagram: State diagram to analyze
        
    Returns:
        Dict[from_state][to_state] = is_implemented
    """
    matrix: Dict[str, Dict[str, bool]] = {}
    implemented = {(t.from_state, t.to_state) for t in diagram.transitions}
    
    for from_state in sorted(diagram.states):
        matrix[from_state] = {}
        for to_state in sorted(diagram.states):
            matrix[from_state][to_state] = (from_state, to_state) in implemented
    
    return matrix


def scan_file_for_state_issues(file_path: Path) -> List[PatternFinding]:
    """Scan a file for state transition issues.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of state-related findings
    """
    findings: List[PatternFinding] = []
    
    diagram = extract_state_machine(file_path)
    if diagram:
        file_findings = analyze_state_gaps(diagram)
        for finding in file_findings:
            finding.file_path = str(file_path)
        findings.extend(file_findings)
    
    return findings
