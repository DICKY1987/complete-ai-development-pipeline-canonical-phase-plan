"""
Integration Tests for UET Migration
"""
# DOC_ID: DOC-TEST-INTEGRATION-TEST-UET-MIGRATION-120

import pytest
from pathlib import Path
from modules.core_engine.m010001_dag_builder import DAGBuilder
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.parallel_orchestrator import ParallelOrchestrator


def test_dag_to_parallel_execution():
    """Test end-to-end DAG building and parallel execution."""
    workstreams = [
        {'workstream_id': 'ws-1', 'dependencies': []},
        {'workstream_id': 'ws-2', 'dependencies': ['ws-1']},
        {'workstream_id': 'ws-3', 'dependencies': ['ws-1']},
        {'workstream_id': 'ws-4', 'dependencies': ['ws-2', 'ws-3']}
    ]
    
    orchestrator = ParallelOrchestrator(max_workers=2)
    report = orchestrator.execute_phase(workstreams)
    
    assert report['total_workstreams'] == 4
    assert report['successful'] == 4
    assert report['failed'] == 0
    assert report['waves_executed'] == 3
    
    orchestrator.shutdown()


def test_parallel_correctness():
    """Test parallel execution produces correct results."""
    workstreams = [
        {'workstream_id': f'parallel-{i}', 'dependencies': []}
        for i in range(10)
    ]
    
    orchestrator = ParallelOrchestrator(max_workers=4)
    report = orchestrator.execute_phase(workstreams)
    
    assert report['successful'] == 10
    assert report['waves_executed'] == 1
    
    orchestrator.shutdown()


def test_dependency_ordering():
    """Test dependencies are respected in execution order."""
    workstreams = [
        {'workstream_id': 'first', 'dependencies': []},
        {'workstream_id': 'second', 'dependencies': ['first']},
        {'workstream_id': 'third', 'dependencies': ['second']}
    ]
    
    builder = DAGBuilder()
    plan = builder.build_from_workstreams(workstreams)
    
    assert plan['waves'][0] == ['first']
    assert plan['waves'][1] == ['second']
    assert plan['waves'][2] == ['third']
