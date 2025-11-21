#!/usr/bin/env python3
"""
Test Suite for Dependency Resolution - PH-3C
"""

import json
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "orchestrator"))

from dependency_resolver import DependencyResolver
from parallel_executor import ParallelExecutor


class TestDependencyResolver:
    """Test dependency resolution."""
    
    @pytest.fixture
    def simple_plan(self, tmp_path):
        """Create a simple phase plan."""
        plan = {
            "phases": [
                {"phase_id": "PH-A", "dependencies": []},
                {"phase_id": "PH-B", "dependencies": ["PH-A"]},
                {"phase_id": "PH-C", "dependencies": ["PH-A"]},
                {"phase_id": "PH-D", "dependencies": ["PH-B", "PH-C"]}
            ]
        }
        
        plan_file = tmp_path / "plan.json"
        with open(plan_file, 'w') as f:
            json.dump(plan, f)
        
        return str(plan_file)
    
    @pytest.fixture
    def circular_plan(self, tmp_path):
        """Create a plan with circular dependencies."""
        plan = {
            "phases": [
                {"phase_id": "PH-A", "dependencies": ["PH-C"]},
                {"phase_id": "PH-B", "dependencies": ["PH-A"]},
                {"phase_id": "PH-C", "dependencies": ["PH-B"]}
            ]
        }
        
        plan_file = tmp_path / "circular.json"
        with open(plan_file, 'w') as f:
            json.dump(plan, f)
        
        return str(plan_file)
    
    def test_load_phase_plan(self, simple_plan):
        """Test loading phase plan."""
        resolver = DependencyResolver()
        success = resolver.load_phase_plan(simple_plan)
        
        assert success is True
        assert len(resolver.phases) == 4
        assert "PH-A" in resolver.phases
    
    def test_dependency_graph_building(self, simple_plan):
        """Test dependency graph construction."""
        resolver = DependencyResolver()
        resolver.load_phase_plan(simple_plan)
        
        assert len(resolver.dependencies["PH-A"]) == 0
        assert "PH-A" in resolver.dependencies["PH-B"]
        assert "PH-A" in resolver.dependencies["PH-C"]
        assert "PH-B" in resolver.dependencies["PH-D"]
        assert "PH-C" in resolver.dependencies["PH-D"]
    
    def test_dependents_graph(self, simple_plan):
        """Test reverse dependency graph."""
        resolver = DependencyResolver()
        resolver.load_phase_plan(simple_plan)
        
        assert "PH-B" in resolver.dependents["PH-A"]
        assert "PH-C" in resolver.dependents["PH-A"]
        assert "PH-D" in resolver.dependents["PH-B"]
    
    def test_detect_no_cycles(self, simple_plan):
        """Test cycle detection on acyclic graph."""
        resolver = DependencyResolver()
        resolver.load_phase_plan(simple_plan)
        
        has_cycles, cycles = resolver.detect_cycles()
        
        assert has_cycles is False
        assert len(cycles) == 0
    
    def test_detect_cycles(self, circular_plan):
        """Test cycle detection on cyclic graph."""
        resolver = DependencyResolver()
        resolver.load_phase_plan(circular_plan)
        
        has_cycles, cycles = resolver.detect_cycles()
        
        assert has_cycles is True
        assert len(cycles) > 0
    
    def test_topological_sort(self, simple_plan):
        """Test topological sort for execution order."""
        resolver = DependencyResolver()
        resolver.load_phase_plan(simple_plan)
        
        order = resolver.topological_sort()
        
        assert order is not None
        assert len(order) == 4
        
        # PH-A must come before PH-B and PH-C
        assert order.index("PH-A") < order.index("PH-B")
        assert order.index("PH-A") < order.index("PH-C")
        
        # PH-B and PH-C must come before PH-D
        assert order.index("PH-B") < order.index("PH-D")
        assert order.index("PH-C") < order.index("PH-D")
    
    def test_topological_sort_with_cycles(self, circular_plan):
        """Test topological sort fails with cycles."""
        resolver = DependencyResolver()
        resolver.load_phase_plan(circular_plan)
        
        order = resolver.topological_sort()
        
        assert order is None
    
    def test_find_parallel_groups(self, simple_plan):
        """Test identification of parallel execution groups."""
        resolver = DependencyResolver()
        resolver.load_phase_plan(simple_plan)
        
        groups = resolver.find_parallel_groups()
        
        assert len(groups) > 0
        
        # PH-A should be in first group (no dependencies)
        assert "PH-A" in groups[0]
        
        # PH-B and PH-C can run in parallel (same level)
        level_with_b = next(i for i, g in enumerate(groups) if "PH-B" in g)
        assert "PH-C" in groups[level_with_b]
    
    def test_get_blocked_phases(self, simple_plan):
        """Test finding phases blocked by a failure."""
        resolver = DependencyResolver()
        resolver.load_phase_plan(simple_plan)
        
        blocked = resolver.get_blocked_phases("PH-A")
        
        # If PH-A fails, PH-B, PH-C, and PH-D should be blocked
        assert "PH-B" in blocked
        assert "PH-C" in blocked
        assert "PH-D" in blocked
    
    def test_can_execute(self, simple_plan):
        """Test checking if phase can execute."""
        resolver = DependencyResolver()
        resolver.load_phase_plan(simple_plan)
        
        # PH-A has no dependencies
        assert resolver.can_execute("PH-A", set()) is True
        
        # PH-B needs PH-A
        assert resolver.can_execute("PH-B", set()) is False
        assert resolver.can_execute("PH-B", {"PH-A"}) is True
        
        # PH-D needs both PH-B and PH-C
        assert resolver.can_execute("PH-D", {"PH-B"}) is False
        assert resolver.can_execute("PH-D", {"PH-B", "PH-C"}) is True
    
    def test_get_dependency_info(self, simple_plan):
        """Test getting dependency information."""
        resolver = DependencyResolver()
        resolver.load_phase_plan(simple_plan)
        
        info = resolver.get_dependency_info("PH-D")
        
        assert info["phase_id"] == "PH-D"
        assert len(info["dependencies"]) == 2
        assert "PH-B" in info["dependencies"]
        assert "PH-C" in info["dependencies"]


class TestParallelExecutor:
    """Test parallel execution."""
    
    def test_initialization(self):
        """Test executor initialization."""
        executor = ParallelExecutor(max_workers=2)
        
        assert executor.max_workers == 2
        assert len(executor.execution_log) == 0
    
    def test_execute_group_dry_run(self):
        """Test dry run execution."""
        executor = ParallelExecutor()
        
        results = executor.execute_group(
            "GROUP-TEST",
            ["PH-A", "PH-B", "PH-C"],
            dry_run=True
        )
        
        assert len(results) == 3
        assert all(v is True for v in results.values())
        assert len(executor.execution_log) == 3
    
    def test_execution_log(self):
        """Test execution logging."""
        executor = ParallelExecutor()
        
        executor.execute_group(
            "GROUP-TEST",
            ["PH-A", "PH-B"],
            dry_run=True
        )
        
        log = executor.get_execution_log()
        
        assert len(log) == 2
        assert log[0]["group_id"] == "GROUP-TEST"
        assert "timestamp" in log[0]
    
    def test_save_log(self, tmp_path):
        """Test saving execution log."""
        executor = ParallelExecutor()
        
        executor.execute_group(
            "GROUP-TEST",
            ["PH-A"],
            dry_run=True
        )
        
        log_file = tmp_path / "execution.json"
        executor.save_log(str(log_file))
        
        assert log_file.exists()
        
        with open(log_file, 'r') as f:
            saved_log = json.load(f)
        
        assert len(saved_log) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
