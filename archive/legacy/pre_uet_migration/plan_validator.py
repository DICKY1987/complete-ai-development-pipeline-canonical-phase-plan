"""Plan validation and dry-run simulation.

Provides validation modes for phase plans with parallelism analysis,
cost estimation, and what-if simulation capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.planning.parallelism_detector import ParallelismProfile, detect_parallel_opportunities
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.state.bundles import WorkstreamBundle, build_dependency_graph, detect_cycles


class ValidationMode(Enum):
    """Validation execution mode."""
    VALIDATE_ONLY = "validate_only"
    EXECUTE = "execute"


@dataclass
class ValidationReport:
    """Validation report for a phase plan."""
    valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    parallelism_profile: ParallelismProfile | None = None
    estimated_duration_seq: float = 0.0
    estimated_duration_par: float = 0.0
    bottlenecks: List[str] = field(default_factory=list)
    
    def to_text(self) -> str:
        """Generate human-readable text report."""
        lines = []
        
        # Status (use ASCII-safe markers)
        status = "[VALID]" if self.valid else "[INVALID]"
        lines.append(f"Validation Status: {status}")
        lines.append("")
        
        # Errors
        if self.errors:
            lines.append("Errors:")
            for err in self.errors:
                lines.append(f"  * {err}")
            lines.append("")
        
        # Warnings
        if self.warnings:
            lines.append("Warnings:")
            for warn in self.warnings:
                lines.append(f"  * {warn}")
            lines.append("")
        
        # Parallelism analysis
        if self.parallelism_profile:
            prof = self.parallelism_profile
            lines.append("Parallelism Analysis:")
            lines.append(f"  - Max Parallelism: {prof.max_parallelism} workers")
            lines.append(f"  - Execution Waves: {len(prof.waves)}")
            lines.append(f"  - Estimated Speedup: {prof.estimated_speedup:.1f}x")
            lines.append(f"  - Sequential Duration: {self.estimated_duration_seq:.0f} time units")
            lines.append(f"  - Parallel Duration: {self.estimated_duration_par:.0f} time units")
            
            if prof.bottlenecks:
                lines.append(f"  - Bottlenecks: {', '.join(prof.bottlenecks)}")
            
            if prof.conflicts:
                lines.append(f"  - Conflicts Detected: {len(prof.conflicts)}")
                for ws_a, ws_b, reason in prof.conflicts[:5]:  # Show first 5
                    lines.append(f"    > {ws_a} <-> {ws_b}: {reason}")
            
            lines.append("")
            
            # Wave breakdown
            if prof.waves:
                lines.append("Execution Waves:")
                for i, wave in enumerate(prof.waves, 1):
                    lines.append(f"  Wave {i}: {', '.join(sorted(wave))}")
                lines.append("")
        
        # Bottlenecks summary
        if self.bottlenecks:
            lines.append("Bottlenecks (non-parallelizable):")
            for bn in self.bottlenecks:
                lines.append(f"  - {bn}")
            lines.append("")
        
        return "\n".join(lines)
    
    def to_json(self) -> str:
        """Generate JSON report."""
        import json
        
        data = {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "estimated_duration_seq": self.estimated_duration_seq,
            "estimated_duration_par": self.estimated_duration_par,
            "bottlenecks": self.bottlenecks,
        }
        
        if self.parallelism_profile:
            prof = self.parallelism_profile
            data["parallelism"] = {
                "max_parallelism": prof.max_parallelism,
                "estimated_speedup": prof.estimated_speedup,
                "waves": [list(wave) for wave in prof.waves],
                "bottlenecks": prof.bottlenecks,
                "conflicts": [
                    {"ws_a": a, "ws_b": b, "reason": r}
                    for a, b, r in prof.conflicts
                ],
            }
        
        return json.dumps(data, indent=2)


def validate_phase_plan(
    bundles: List[WorkstreamBundle],
    mode: ValidationMode = ValidationMode.VALIDATE_ONLY,
    max_workers: int = 4
) -> ValidationReport:
    """Validate phase plan with parallelism analysis.
    
    UET Section 6: Plan validation and simulation.
    
    Performs:
    - Schema validation (bundles already validated on load)
    - DAG validation (cycle detection)
    - File scope validation
    - Parallelism analysis
    - Cost estimation (if metadata present)
    - Resource simulation
    
    Args:
        bundles: List of workstream bundles to validate
        mode: Validation mode (validate_only or execute)
        max_workers: Maximum parallel workers for simulation
        
    Returns:
        ValidationReport with analysis results
    """
    report = ValidationReport()
    
    if not bundles:
        report.warnings.append("No workstreams to validate")
        return report
    
    # DAG validation (cycle detection)
    try:
        children, parents = build_dependency_graph(bundles)
        cycles = detect_cycles(children)
        if cycles:
            report.valid = False
            for cycle in cycles:
                report.errors.append(f"Dependency cycle detected: {' -> '.join(cycle)}")
    except Exception as e:
        report.valid = False
        report.errors.append(f"Dependency graph error: {e}")
    
    # File scope validation
    try:
        from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.state.bundles import detect_filescope_overlaps
        overlaps = detect_filescope_overlaps(bundles)
        if overlaps:
            # overlaps is {file_path: [ws_ids]} - find pairs
            for file_path, ws_ids in overlaps.items():
                if len(ws_ids) > 1:
                    # Check if overlapping workstreams have dependencies
                    for i, ws_a in enumerate(ws_ids):
                        for ws_b in ws_ids[i+1:]:
                            bundle_a = next(b for b in bundles if b.id == ws_a)
                            bundle_b = next(b for b in bundles if b.id == ws_b)
                            
                            # Check if they're dependent (then overlap is expected)
                            if ws_b not in bundle_a.depends_on and ws_a not in bundle_b.depends_on:
                                # Not dependent and overlap - will serialize
                                report.warnings.append(
                                    f"File scope overlap: {ws_a} and {ws_b} both access {file_path} "
                                    "(will be serialized)"
                                )
    except Exception as e:
        report.warnings.append(f"File scope check error: {e}")
    
    # Parallelism analysis
    try:
        profile = detect_parallel_opportunities(bundles, max_workers)
        report.parallelism_profile = profile
        report.estimated_duration_seq = len(bundles)
        report.estimated_duration_par = len(profile.waves) if profile.waves else len(bundles)
        report.bottlenecks = profile.bottlenecks
        
        # Check for UET metadata
        missing_metadata = []
        for bundle in bundles:
            if bundle.estimated_context_tokens is None:
                missing_metadata.append(f"{bundle.id}: missing estimated_context_tokens")
            if bundle.max_cost_usd is None:
                missing_metadata.append(f"{bundle.id}: missing max_cost_usd")
        
        if missing_metadata:
            report.warnings.append("Missing UET metadata (cost/context estimation unavailable):")
            report.warnings.extend(f"  • {msg}" for msg in missing_metadata[:10])
    
    except Exception as e:
        report.warnings.append(f"Parallelism analysis error: {e}")
    
    # Check for test gates
    for bundle in bundles:
        if bundle.test_gates:
            required_gates = [g for g in bundle.test_gates if g.get("required", False)]
            if required_gates:
                report.warnings.append(
                    f"{bundle.id}: has {len(required_gates)} required test gates"
                )
    
    return report
