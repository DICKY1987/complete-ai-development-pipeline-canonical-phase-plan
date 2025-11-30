"""Parallelism detection and analysis.

This module analyzes workstream bundles to identify parallel execution opportunities
based on DAG topology, file scope conflicts, and UET metadata.
"""
DOC_ID: DOC-PAT-CORE-PLANNING-PARALLELISM-DETECTOR-407

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from modules.core_state.m010003_bundles import WorkstreamBundle


@dataclass
class ParallelismProfile:
    """Analysis of parallel execution opportunities."""
    waves: List[Set[str]] = field(default_factory=list)  # Execution waves
    bottlenecks: List[str] = field(default_factory=list)
    max_parallelism: int = 1
    estimated_speedup: float = 1.0
    conflicts: List[Tuple[str, str, str]] = field(default_factory=list)  # (ws_a, ws_b, reason)


def detect_parallel_opportunities(
    bundles: List[WorkstreamBundle],
    max_workers: int = 4
) -> ParallelismProfile:
    """Analyze DAG and file scopes to identify parallelism.
    
    Algorithm:
    1. Topological sort into dependency levels
    2. Within each level, group by file scope conflicts
    3. Respect conflict_group serialization
    4. Calculate theoretical speedup
    
    Args:
        bundles: List of workstream bundles to analyze
        max_workers: Maximum number of parallel workers
        
    Returns:
        ParallelismProfile with waves and speedup estimates
    """
    profile = ParallelismProfile()
    
    if not bundles:
        return profile
    
    # Build dependency graph
    bundle_map = {b.id: b for b in bundles}
    dep_graph: Dict[str, Set[str]] = {b.id: set(b.depends_on) for b in bundles}
    
    # Topological sort into levels
    levels = _topological_levels(dep_graph, bundle_map)
    
    # Build waves from levels respecting constraints
    for level in levels:
        level_bundles = [bundle_map[ws_id] for ws_id in level]
        waves = _partition_into_waves(level_bundles, max_workers, profile)
        profile.waves.extend(waves)
    
    # Calculate metrics
    profile.max_parallelism = max(len(wave) for wave in profile.waves) if profile.waves else 1
    profile.estimated_speedup = _calculate_speedup(profile, len(bundles))
    profile.bottlenecks = _identify_bottlenecks(profile, bundle_map)
    
    return profile


def detect_conflict_groups(bundles: List[WorkstreamBundle]) -> Dict[str, List[str]]:
    """Group workstreams by conflict_group metadata.
    
    Args:
        bundles: List of workstream bundles
        
    Returns:
        Dict mapping conflict_group names to workstream IDs
    """
    groups: Dict[str, List[str]] = {}
    
    for bundle in bundles:
        if bundle.conflict_group:
            if bundle.conflict_group not in groups:
                groups[bundle.conflict_group] = []
            groups[bundle.conflict_group].append(bundle.id)
    
    return groups


def _topological_levels(
    dep_graph: Dict[str, Set[str]],
    bundle_map: Dict[str, WorkstreamBundle]
) -> List[Set[str]]:
    """Perform topological sort into dependency levels.
    
    Returns list of sets, where each set contains workstream IDs
    that can potentially run in parallel (same dependency level).
    """
    levels: List[Set[str]] = []
    remaining = set(dep_graph.keys())
    completed: Set[str] = set()
    
    while remaining:
        # Find workstreams with all dependencies completed
        ready = {
            ws_id for ws_id in remaining
            if dep_graph[ws_id].issubset(completed)
        }
        
        if not ready:
            # Circular dependency or missing dependency
            break
        
        levels.append(ready)
        completed.update(ready)
        remaining -= ready
    
    return levels


def _partition_into_waves(
    level_bundles: List[WorkstreamBundle],
    max_workers: int,
    profile: ParallelismProfile
) -> List[Set[str]]:
    """Partition a dependency level into execution waves.
    
    Constraints:
    - File scope conflicts prevent parallel execution
    - conflict_group enforces serialization
    - parallel_ok=False forces serialization
    - Wave size limited by max_workers
    """
    waves: List[Set[str]] = []
    remaining = list(level_bundles)
    
    while remaining:
        wave: Set[str] = set()
        wave_bundles: List[WorkstreamBundle] = []
        conflict_groups_used: Set[str] = set()
        file_scopes_used: Set[str] = set()
        
        for bundle in remaining[:]:
            # Check parallel_ok flag
            if not bundle.parallel_ok:
                # Must run alone
                if not wave:
                    wave.add(bundle.id)
                    wave_bundles.append(bundle)
                    remaining.remove(bundle)
                    break
                continue
            
            # Check conflict_group
            if bundle.conflict_group:
                if bundle.conflict_group in conflict_groups_used:
                    profile.conflicts.append(
                        (list(wave)[0], bundle.id, f"conflict_group:{bundle.conflict_group}")
                    )
                    continue
            
            # Check file scope conflicts
            bundle_files = set(bundle.files_scope)
            if bundle_files & file_scopes_used:
                conflicting = [b.id for b in wave_bundles if set(b.files_scope) & bundle_files]
                if conflicting:
                    profile.conflicts.append(
                        (conflicting[0], bundle.id, f"file_scope:{bundle_files & file_scopes_used}")
                    )
                    continue
            
            # Check wave size limit
            if len(wave) >= max_workers:
                continue
            
            # Add to wave
            wave.add(bundle.id)
            wave_bundles.append(bundle)
            remaining.remove(bundle)
            
            if bundle.conflict_group:
                conflict_groups_used.add(bundle.conflict_group)
            file_scopes_used.update(bundle.files_scope)
        
        if wave:
            waves.append(wave)
        else:
            # No progress - force one workstream
            if remaining:
                bundle = remaining.pop(0)
                waves.append({bundle.id})
    
    return waves


def _calculate_speedup(profile: ParallelismProfile, total_workstreams: int) -> float:
    """Calculate theoretical speedup from parallel execution.
    
    Speedup = sequential_time / parallel_time
    Assumes each workstream takes 1 time unit.
    """
    if not profile.waves:
        return 1.0
    
    # Sequential time: sum of all workstreams
    sequential_time = total_workstreams
    
    # Parallel time: number of waves (each wave runs in parallel)
    parallel_time = len(profile.waves)
    
    if parallel_time == 0:
        return 1.0
    
    return sequential_time / parallel_time


def _identify_bottlenecks(
    profile: ParallelismProfile,
    bundle_map: Dict[str, WorkstreamBundle]
) -> List[str]:
    """Identify bottleneck workstreams that limit parallelism.
    
    Bottlenecks are workstreams that:
    - Run alone in a wave (parallel_ok=False or conflicts)
    - Have many dependents
    """
    bottlenecks: List[str] = []
    
    for wave in profile.waves:
        if len(wave) == 1:
            ws_id = list(wave)[0]
            bundle = bundle_map.get(ws_id)
            if bundle and not bundle.parallel_ok:
                bottlenecks.append(ws_id)
    
    return bottlenecks
