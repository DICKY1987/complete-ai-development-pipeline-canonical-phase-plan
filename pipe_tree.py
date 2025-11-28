#!/usr/bin/env python3
"""
PIPELINE_RESTRUCTURE_TREE_SPEC_V1 Implementation

Generates a virtual file tree showing how the current repository would look
if reorganized around PIPE-01 to PIPE-26 pipeline structure.

Usage:
    python pipe_tree.py [options]

Options:
    --root PATH              Repository root directory (default: current directory)
    --mapping-config PATH    Path to pipe_mapping_config.yaml (default: pipe_mapping_config.yaml)
    --ignore-file PATH       Path to ignore patterns file (default: .pipeignore)
    --output PATH            Output file path (default: PIPELINE_VIRTUAL_TREE.txt)
    --help                   Show this help message
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
import fnmatch
import yaml


# ============================================================================
# CANONICAL PIPE STRUCTURE
# ============================================================================

MACRO_PHASES = {
    "A": "A_INTAKE_AND_SPECS",
    "B": "B_WORKSTREAM_AND_CONFIG",
    "C": "C_PATTERNS_AND_PLANNING",
    "D": "D_WORKSPACE_AND_SCHEDULING",
    "E": "E_EXECUTION_AND_VALIDATION",
    "F": "F_ERROR_AND_RECOVERY",
    "G": "G_FINALIZATION_AND_LEARNING",
}

PIPE_MODULES = {
    # A: INTAKE AND SPECS
    "PIPE-01_INTAKE_REQUEST": "A",
    "PIPE-02_DISCOVER_RELATED_SPECS": "A",
    "PIPE-03_NORMALIZE_REQUIREMENTS": "A",
    
    # B: WORKSTREAM AND CONFIG
    "PIPE-04_MATERIALIZE_WORKSTREAM_FILE": "B",
    "PIPE-05_VALIDATE_WORKSTREAM_SCHEMA": "B",
    "PIPE-06_RESOLVE_CONFIG_CASCADE": "B",
    "PIPE-07_RESOLVE_CAPABILITIES_AND_REGISTRY": "B",
    
    # C: PATTERNS AND PLANNING
    "PIPE-08_SELECT_UET_PATTERNS": "C",
    "PIPE-09_SPECIALIZE_PATTERNS_WITH_CONTEXT": "C",
    "PIPE-10_VALIDATE_PATTERN_PLAN": "C",
    "PIPE-11_BUILD_TASK_GRAPH_DAG": "C",
    "PIPE-12_PERSIST_PLAN_IN_STATE": "C",
    
    # D: WORKSPACE AND SCHEDULING
    "PIPE-13_PREPARE_WORKTREES_AND_CHECKPOINTS": "D",
    "PIPE-14_ADMIT_READY_TASKS_TO_QUEUE": "D",
    "PIPE-15_ASSIGN_PRIORITIES_AND_SLOTS": "D",
    
    # E: EXECUTION AND VALIDATION
    "PIPE-16_ROUTE_TASK_TO_TOOL_ADAPTER": "E",
    "PIPE-17_EXECUTE_TOOL_AND_CAPTURE_OUTPUT": "E",
    "PIPE-18_RUN_POST_EXEC_TESTS_AND_CHECKS": "E",
    
    # F: ERROR AND RECOVERY
    "PIPE-19_RUN_ERROR_PLUGINS_PIPELINE": "F",
    "PIPE-20_CLASSIFY_ERRORS_AND_CHOOSE_ACTION": "F",
    "PIPE-21_APPLY_AUTOFIX_RETRY_AND_CIRCUIT_CONTROL": "F",
    
    # G: FINALIZATION AND LEARNING
    "PIPE-22_COMMIT_TASK_RESULTS_TO_STATE_AND_MODULES": "G",
    "PIPE-23_COMPLETE_WORKSTREAM_AND_ARCHIVE": "G",
    "PIPE-24_UPDATE_METRICS_REPORTS_AND_SUMMARIES": "G",
    "PIPE-25_SURFACE_TO_GUI_AND_TUI": "G",
    "PIPE-26_LEARN_AND_UPDATE_PATTERNS_PROMPTS_CONFIG": "G",
}


# ============================================================================
# TREE NODE
# ============================================================================

class TreeNode:
    """Represents a node in the virtual tree structure."""
    
    def __init__(self, name: str, is_directory: bool = True):
        self.name = name
        self.is_directory = is_directory
        self.children: List[TreeNode] = []
    
    def add_child(self, child: 'TreeNode'):
        """Add a child node."""
        self.children.append(child)
    
    def sort_children(self):
        """Sort children: directories first, then files, alphabetically."""
        self.children.sort(key=lambda n: (not n.is_directory, n.name))
        for child in self.children:
            if child.is_directory:
                child.sort_children()


# ============================================================================
# IGNORE PATTERN MATCHER
# ============================================================================

class IgnoreMatcher:
    """Handles .pipeignore pattern matching."""
    
    def __init__(self, patterns: List[str]):
        self.patterns = [p.strip() for p in patterns if p.strip() and not p.startswith('#')]
    
    def should_ignore(self, path: str) -> bool:
        """Check if path matches any ignore pattern."""
        path_normalized = path.replace('\\', '/')
        
        for pattern in self.patterns:
            # Directory patterns end with /
            if pattern.endswith('/'):
                if path_normalized.startswith(pattern.rstrip('/') + '/'):
                    return True
                if path_normalized == pattern.rstrip('/'):
                    return True
            # Wildcard patterns
            elif '*' in pattern:
                if fnmatch.fnmatch(path_normalized, pattern):
                    return True
            # Exact match
            else:
                if path_normalized == pattern or path_normalized.startswith(pattern + '/'):
                    return True
        
        return False


# ============================================================================
# PIPE CLASSIFIER
# ============================================================================

class PipeClassifier:
    """Classifies files into PIPE modules based on mapping rules."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.rules = config.get('rules', [])
        self.default_pipe_id = config.get('default_pipe_id', 'PIPE-26_LEARN_AND_UPDATE_PATTERNS_PROMPTS_CONFIG')
    
    def classify(self, relative_path: str) -> str:
        """
        Classify a file path to a PIPE module ID.
        Returns PIPE-XX_NAME string.
        """
        path_normalized = relative_path.replace('\\', '/')
        
        # Apply rules in order (first match wins)
        for rule in self.rules:
            if self._rule_matches(path_normalized, rule):
                return rule['pipe_id']
        
        # No match - use default
        return self.default_pipe_id
    
    def _rule_matches(self, path: str, rule: Dict) -> bool:
        """Check if path matches a rule."""
        match = rule.get('match', {})
        
        # Check path_prefix
        for prefix in match.get('path_prefix', []):
            prefix_normalized = prefix.replace('\\', '/')
            if path.startswith(prefix_normalized):
                return True
        
        # Check file_glob
        for glob in match.get('file_glob', []):
            glob_normalized = glob.replace('\\', '/')
            if fnmatch.fnmatch(path, glob_normalized):
                return True
        
        return False


# ============================================================================
# TREE BUILDER
# ============================================================================

class TreeBuilder:
    """Builds the virtual pipeline tree structure."""
    
    def __init__(self):
        self.root = TreeNode("pipeline", is_directory=True)
        self.phase_nodes: Dict[str, TreeNode] = {}
        self.pipe_nodes: Dict[str, TreeNode] = {}
        
        # Create fixed structure
        self._create_structure()
    
    def _create_structure(self):
        """Create the fixed pipeline structure."""
        # Create macro phase directories
        for phase_code, phase_name in MACRO_PHASES.items():
            phase_node = TreeNode(phase_name, is_directory=True)
            self.root.add_child(phase_node)
            self.phase_nodes[phase_code] = phase_node
        
        # Create PIPE module directories
        for pipe_id, phase_code in PIPE_MODULES.items():
            pipe_node = TreeNode(pipe_id, is_directory=True)
            self.phase_nodes[phase_code].add_child(pipe_node)
            self.pipe_nodes[pipe_id] = pipe_node
    
    def add_file(self, pipe_id: str, original_path: str):
        """Add a file (as leaf node) to the appropriate PIPE module."""
        if pipe_id in self.pipe_nodes:
            file_node = TreeNode(original_path, is_directory=False)
            self.pipe_nodes[pipe_id].add_child(file_node)
        else:
            print(f"Warning: Unknown PIPE ID '{pipe_id}' for file '{original_path}'", file=sys.stderr)
    
    def finalize(self):
        """Sort all nodes in the tree."""
        self.root.sort_children()


# ============================================================================
# TREE RENDERER
# ============================================================================

class TreeRenderer:
    """Renders the tree as ASCII text."""
    
    def render(self, root: TreeNode) -> str:
        """Render tree starting from root node."""
        lines = []
        self._render_node(root, lines, prefix="", is_last=True)
        return "\n".join(lines)
    
    def _render_node(self, node: TreeNode, lines: List[str], prefix: str, is_last: bool):
        """Recursively render a node and its children."""
        # Root node special case
        if prefix == "":
            lines.append(node.name + "/" if node.is_directory else node.name)
            for i, child in enumerate(node.children):
                is_last_child = (i == len(node.children) - 1)
                self._render_node(child, lines, "  ", is_last_child)
            return
        
        # Build connector
        connector = "" if is_last else ""
        
        # Add current node
        suffix = "/" if node.is_directory else ""
        lines.append(f"{prefix}{node.name}{suffix}")
        
        # Render children
        if node.is_directory and node.children:
            new_prefix = prefix + "  "
            for i, child in enumerate(node.children):
                is_last_child = (i == len(node.children) - 1)
                self._render_node(child, lines, new_prefix, is_last_child)


# ============================================================================
# FILE DISCOVERY
# ============================================================================

def discover_files(root_dir: Path, ignore_matcher: IgnoreMatcher) -> List[str]:
    """
    Recursively discover all files in root_dir.
    Returns list of relative paths.
    """
    files = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Compute relative path
        rel_dir = os.path.relpath(dirpath, root_dir)
        if rel_dir == '.':
            rel_dir = ''
        
        # Filter directories in-place to skip ignored ones
        dirnames[:] = [
            d for d in dirnames
            if not ignore_matcher.should_ignore(os.path.join(rel_dir, d) if rel_dir else d)
        ]
        
        # Add files
        for filename in filenames:
            rel_path = os.path.join(rel_dir, filename) if rel_dir else filename
            if not ignore_matcher.should_ignore(rel_path):
                files.append(rel_path)
    
    return files


# ============================================================================
# MAIN
# ============================================================================

def load_yaml(path: Path) -> Dict:
    """Load YAML file."""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_ignore_patterns(path: Path) -> List[str]:
    """Load ignore patterns from file."""
    if not path.exists():
        return []
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.readlines()


def main():
    parser = argparse.ArgumentParser(
        description="Generate virtual PIPE-01 to PIPE-26 tree structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--root',
        type=Path,
        default=Path('.'),
        help='Repository root directory (default: current directory)'
    )
    
    parser.add_argument(
        '--mapping-config',
        type=Path,
        default=Path('pipe_mapping_config.yaml'),
        help='Path to pipe_mapping_config.yaml (default: pipe_mapping_config.yaml)'
    )
    
    parser.add_argument(
        '--ignore-file',
        type=Path,
        default=Path('.pipeignore'),
        help='Path to ignore patterns file (default: .pipeignore)'
    )
    
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('PIPELINE_VIRTUAL_TREE.txt'),
        help='Output file path (default: PIPELINE_VIRTUAL_TREE.txt)'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.root.exists():
        print(f"Error: Root directory does not exist: {args.root}", file=sys.stderr)
        return 1
    
    if not args.mapping_config.exists():
        print(f"Error: Mapping config file does not exist: {args.mapping_config}", file=sys.stderr)
        return 1
    
    # Load configuration
    print(f"Loading mapping config from {args.mapping_config}...")
    config = load_yaml(args.mapping_config)
    
    print(f"Loading ignore patterns from {args.ignore_file}...")
    ignore_patterns = load_ignore_patterns(args.ignore_file)
    ignore_matcher = IgnoreMatcher(ignore_patterns)
    
    # Initialize components
    classifier = PipeClassifier(config)
    tree_builder = TreeBuilder()
    
    # Discover files
    print(f"Discovering files in {args.root}...")
    files = discover_files(args.root, ignore_matcher)
    print(f"Found {len(files)} files to classify")
    
    # Classify and build tree
    print("Classifying files into PIPE modules...")
    for file_path in files:
        pipe_id = classifier.classify(file_path)
        tree_builder.add_file(pipe_id, file_path)
    
    # Finalize tree
    print("Building tree structure...")
    tree_builder.finalize()
    
    # Render tree
    print("Rendering tree...")
    renderer = TreeRenderer()
    tree_text = renderer.render(tree_builder.root)
    
    # Write output
    print(f"Writing output to {args.output}...")
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(tree_text)
        f.write('\n')
    
    print(f"Done! Virtual tree written to {args.output}")
    print(f"Total files mapped: {len(files)}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
