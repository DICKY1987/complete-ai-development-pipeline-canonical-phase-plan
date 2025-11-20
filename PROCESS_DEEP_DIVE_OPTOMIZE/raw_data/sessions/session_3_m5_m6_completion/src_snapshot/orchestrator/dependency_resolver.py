#!/usr/bin/env python3
"""
Dependency Resolver - PH-3C

Builds dependency graph (DAG) and determines execution order.
Identifies parallel execution opportunities.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque


class DependencyResolver:
    """Resolves phase dependencies and determines execution order."""
    
    def __init__(self):
        self.phases: Dict[str, Dict] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.dependents: Dict[str, Set[str]] = defaultdict(set)
    
    def load_phase_plan(self, plan_file: str) -> bool:
        """
        Load phase plan from JSON file.
        
        Args:
            plan_file: Path to master phase plan
        
        Returns:
            True if loaded successfully
        """
        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                plan = json.load(f)
            
            # Extract phase information
            for phase_entry in plan.get("phases", []):
                phase_id = phase_entry.get("phase_id")
                if not phase_id:
                    continue
                
                # Load actual spec if available
                spec_file = phase_entry.get("spec_file")
                if spec_file and Path(spec_file).exists():
                    with open(spec_file, 'r') as sf:
                        spec = json.load(sf)
                        self.phases[phase_id] = spec
                else:
                    self.phases[phase_id] = phase_entry
                
                # Build dependency graph
                deps = self.phases[phase_id].get("dependencies", [])
                for dep in deps:
                    self.dependencies[phase_id].add(dep)
                    self.dependents[dep].add(phase_id)
            
            return True
        
        except Exception as e:
            print(f"Error loading phase plan: {e}", file=sys.stderr)
            return False
    
    def detect_cycles(self) -> Tuple[bool, List[str]]:
        """
        Detect circular dependencies using DFS.
        
        Returns:
            Tuple of (has_cycles, cycle_paths)
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {phase: WHITE for phase in self.phases}
        parent = {}
        cycles = []
        
        def dfs(node: str, path: List[str]) -> bool:
            """DFS to detect cycles."""
            color[node] = GRAY
            path.append(node)
            
            for dep in self.dependencies[node]:
                if dep not in color:
                    continue
                
                if color[dep] == GRAY:
                    # Found a cycle
                    cycle_start = path.index(dep)
                    cycle = path[cycle_start:] + [dep]
                    cycles.append(" → ".join(cycle))
                    return True
                
                elif color[dep] == WHITE:
                    if dfs(dep, path.copy()):
                        return True
            
            color[node] = BLACK
            return False
        
        for phase in self.phases:
            if color[phase] == WHITE:
                dfs(phase, [])
        
        return len(cycles) > 0, cycles
    
    def topological_sort(self) -> Optional[List[str]]:
        """
        Perform topological sort to get execution order.
        
        Returns:
            List of phase IDs in execution order, or None if cycles exist
        """
        has_cycles, _ = self.detect_cycles()
        if has_cycles:
            return None
        
        # Kahn's algorithm
        in_degree = {phase: len(self.dependencies[phase]) for phase in self.phases}
        queue = deque([phase for phase, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            phase = queue.popleft()
            result.append(phase)
            
            for dependent in self.dependents[phase]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        return result if len(result) == len(self.phases) else None
    
    def find_parallel_groups(self) -> List[List[str]]:
        """
        Identify groups of phases that can execute in parallel.
        
        Returns:
            List of parallel execution groups
        """
        order = self.topological_sort()
        if not order:
            return []
        
        # Assign levels based on longest path from roots
        levels: Dict[str, int] = {}
        
        def get_level(phase: str) -> int:
            """Get execution level for a phase."""
            if phase in levels:
                return levels[phase]
            
            if not self.dependencies[phase]:
                levels[phase] = 0
                return 0
            
            max_dep_level = max(get_level(dep) for dep in self.dependencies[phase])
            levels[phase] = max_dep_level + 1
            return levels[phase]
        
        for phase in order:
            get_level(phase)
        
        # Group phases by level
        groups_by_level: Dict[int, List[str]] = defaultdict(list)
        for phase, level in levels.items():
            groups_by_level[level].append(phase)
        
        # Convert to list of groups
        max_level = max(groups_by_level.keys()) if groups_by_level else 0
        groups = []
        for level in range(max_level + 1):
            if level in groups_by_level and len(groups_by_level[level]) > 0:
                groups.append(sorted(groups_by_level[level]))
        
        return groups
    
    def get_blocked_phases(self, failed_phase: str) -> Set[str]:
        """
        Get all phases blocked by a failed phase.
        
        Args:
            failed_phase: Phase that failed
        
        Returns:
            Set of blocked phase IDs
        """
        blocked = set()
        queue = deque([failed_phase])
        
        while queue:
            phase = queue.popleft()
            for dependent in self.dependents[phase]:
                if dependent not in blocked:
                    blocked.add(dependent)
                    queue.append(dependent)
        
        return blocked
    
    def can_execute(self, phase_id: str, completed: Set[str]) -> bool:
        """
        Check if a phase can execute given completed phases.
        
        Args:
            phase_id: Phase to check
            completed: Set of completed phase IDs
        
        Returns:
            True if all dependencies are satisfied
        """
        return all(dep in completed for dep in self.dependencies[phase_id])
    
    def get_dependency_info(self, phase_id: str) -> Dict:
        """
        Get dependency information for a phase.
        
        Args:
            phase_id: Phase identifier
        
        Returns:
            Dictionary with dependency info
        """
        return {
            "phase_id": phase_id,
            "dependencies": sorted(list(self.dependencies[phase_id])),
            "dependents": sorted(list(self.dependents[phase_id])),
            "dependency_count": len(self.dependencies[phase_id]),
            "dependent_count": len(self.dependents[phase_id])
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Dependency resolver for phase execution"
    )
    parser.add_argument(
        "--plan",
        type=str,
        required=True,
        help="Path to master phase plan JSON"
    )
    parser.add_argument(
        "--build-graph",
        action="store_true",
        help="Build and display dependency graph"
    )
    parser.add_argument(
        "--check-cycles",
        action="store_true",
        help="Check for circular dependencies"
    )
    parser.add_argument(
        "--execution-order",
        action="store_true",
        help="Show topological execution order"
    )
    parser.add_argument(
        "--find-parallel",
        action="store_true",
        help="Identify parallel execution groups"
    )
    parser.add_argument(
        "--simulate-failure",
        type=str,
        help="Simulate phase failure"
    )
    parser.add_argument(
        "--check-blocked",
        action="store_true",
        help="Check which phases are blocked (use with --simulate-failure)"
    )
    parser.add_argument(
        "--phase-info",
        type=str,
        help="Get dependency info for specific phase"
    )
    
    args = parser.parse_args()
    
    try:
        resolver = DependencyResolver()
        
        if not resolver.load_phase_plan(args.plan):
            return 1
        
        if args.build_graph:
            print(f"\nDependency Graph ({len(resolver.phases)} phases):")
            for phase_id in sorted(resolver.phases.keys()):
                deps = resolver.dependencies[phase_id]
                if deps:
                    print(f"  {phase_id} depends on: {', '.join(sorted(deps))}")
                else:
                    print(f"  {phase_id} (no dependencies)")
            return 0
        
        if args.check_cycles:
            has_cycles, cycles = resolver.detect_cycles()
            if has_cycles:
                print("✗ Circular dependencies detected:")
                for cycle in cycles:
                    print(f"  {cycle}")
                return 1
            else:
                print("✓ No circular dependencies")
                return 0
        
        if args.execution_order:
            order = resolver.topological_sort()
            if order:
                print("\nExecution Order:")
                for i, phase in enumerate(order, 1):
                    print(f"  {i}. {phase}")
                return 0
            else:
                print("✗ Cannot determine execution order (cycles exist)")
                return 1
        
        if args.find_parallel:
            groups = resolver.find_parallel_groups()
            print(f"\nParallel Execution Groups: {len(groups)}")
            for i, group in enumerate(groups, 1):
                print(f"  Group {i}: {', '.join(group)}")
            return 0
        
        if args.simulate_failure and args.check_blocked:
            blocked = resolver.get_blocked_phases(args.simulate_failure)
            print(f"\nPhases blocked by {args.simulate_failure}:")
            for phase in sorted(blocked):
                print(f"  {phase}")
            return 0
        
        if args.phase_info:
            info = resolver.get_dependency_info(args.phase_info)
            print(json.dumps(info, indent=2))
            return 0
        
        parser.print_help()
        return 1
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
