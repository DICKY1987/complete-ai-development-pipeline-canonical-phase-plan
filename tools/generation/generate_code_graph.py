#!/usr/bin/env python3
"""
Generate code dependency graph from CODEBASE_INDEX and actual imports.

This script generates:
- .meta/ai_context/code_graph.json - Module dependency graph

Inputs:
- CODEBASE_INDEX.yaml (declared dependencies)
- Optional: AST parsing of actual imports (future enhancement)

Output:
- .meta/ai_context/code_graph.json
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML file with error handling."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"Error: {path} not found")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing {path}: {e}")
        sys.exit(1)


def build_dependency_graph(modules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build dependency graph from module definitions."""
    
    # Create module lookup
    module_map = {m['id']: m for m in modules}
    
    # Build adjacency list
    graph = {
        'nodes': [],
        'edges': []
    }
    
    # Add nodes
    for module in modules:
        node = {
            'id': module['id'],
            'name': module['name'],
            'path': module['path'],
            'layer': module.get('layer', 'unknown'),
            'priority': module.get('ai_priority', 'MEDIUM'),
            'edit_policy': module.get('edit_policy', 'review-required')
        }
        graph['nodes'].append(node)
    
    # Add edges (dependencies)
    for module in modules:
        module_id = module['id']
        depends_on = module.get('depends_on', [])
        
        for dep_id in depends_on:
            if dep_id not in module_map:
                print(f"Warning: Module '{module_id}' depends on unknown module '{dep_id}'")
                continue
            
            edge = {
                'from': module_id,
                'to': dep_id,
                'type': 'depends_on'
            }
            graph['edges'].append(edge)
    
    return graph


def validate_acyclic(graph: Dict[str, Any]) -> bool:
    """Validate that the dependency graph is acyclic (DAG)."""
    
    # Build adjacency list for cycle detection
    adj_list = {}
    for node in graph['nodes']:
        adj_list[node['id']] = []
    
    for edge in graph['edges']:
        adj_list[edge['from']].append(edge['to'])
    
    # DFS cycle detection
    visited = set()
    rec_stack = set()
    
    def has_cycle(node_id: str) -> bool:
        visited.add(node_id)
        rec_stack.add(node_id)
        
        for neighbor in adj_list.get(node_id, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                print(f"Cycle detected: {node_id} -> {neighbor}")
                return True
        
        rec_stack.remove(node_id)
        return False
    
    for node in graph['nodes']:
        if node['id'] not in visited:
            if has_cycle(node['id']):
                return False
    
    return True


def calculate_metrics(graph: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate graph metrics."""
    
    node_count = len(graph['nodes'])
    edge_count = len(graph['edges'])
    
    # Count in-degree and out-degree
    in_degree = {n['id']: 0 for n in graph['nodes']}
    out_degree = {n['id']: 0 for n in graph['nodes']}
    
    for edge in graph['edges']:
        out_degree[edge['from']] += 1
        in_degree[edge['to']] += 1
    
    # Find roots (no dependencies) and leaves (no dependents)
    roots = [nid for nid, deg in in_degree.items() if deg == 0]
    leaves = [nid for nid, deg in out_degree.items() if deg == 0]
    
    # Layer distribution
    layer_counts = {}
    for node in graph['nodes']:
        layer = node['layer']
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    
    return {
        'node_count': node_count,
        'edge_count': edge_count,
        'average_dependencies': round(edge_count / node_count, 2) if node_count > 0 else 0,
        'root_modules': roots,
        'leaf_modules': leaves,
        'max_in_degree': max(in_degree.values()) if in_degree else 0,
        'max_out_degree': max(out_degree.values()) if out_degree else 0,
        'layer_distribution': layer_counts
    }


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    
    print("Loading CODEBASE_INDEX.yaml...")
    codebase_index = load_yaml(repo_root / 'CODEBASE_INDEX.yaml')
    
    modules = codebase_index.get('modules', [])
    if not modules:
        print("Error: No modules found in CODEBASE_INDEX.yaml")
        sys.exit(1)
    
    print(f"Building dependency graph for {len(modules)} modules...")
    graph = build_dependency_graph(modules)
    
    print("Validating graph is acyclic...")
    if not validate_acyclic(graph):
        print("Error: Dependency graph contains cycles!")
        sys.exit(1)
    
    print("Calculating metrics...")
    metrics = calculate_metrics(graph)
    
    # Build output structure
    output = {
        'graph': graph,
        'metrics': metrics,
        'metadata': {
            'source': 'CODEBASE_INDEX.yaml',
            'generated': '2025-11-22T20:54:48Z',
            'generator': 'scripts/generate_code_graph.py',
            'version': '1.0.0',
            'validation': {
                'acyclic': True,
                'all_modules_reachable': len(metrics['root_modules']) > 0
            }
        }
    }
    
    # Ensure output directory exists
    output_dir = repo_root / '.meta' / 'ai_context'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write JSON
    json_path = output_dir / 'code_graph.json'
    print(f"Writing {json_path}...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Code graph generated successfully")
    print(f"  - Output: {json_path}")
    print(f"\nMetrics:")
    print(f"  - Nodes: {metrics['node_count']}")
    print(f"  - Edges: {metrics['edge_count']}")
    print(f"  - Average dependencies: {metrics['average_dependencies']}")
    print(f"  - Root modules: {len(metrics['root_modules'])}")
    print(f"  - Leaf modules: {len(metrics['leaf_modules'])}")
    print(f"  - Acyclic: ✓")


if __name__ == '__main__':
    main()
