"""
Base extractor classes for language-specific AST analysis.

Provides abstract interfaces that language-specific extractors must implement.
"""
# DOC_ID: DOC-CORE-AST-EXTRACTORS-137

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from tree_sitter import Node, Tree


@dataclass
class FunctionInfo:
    """Information extracted from a function definition."""
    name: str
    start_line: int
    end_line: int
    params: List[str]
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    decorators: List[str] = None
    is_async: bool = False
    
    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []


@dataclass
class ClassInfo:
    """Information extracted from a class definition."""
    name: str
    start_line: int
    end_line: int
    bases: List[str]
    methods: List[str]
    docstring: Optional[str] = None
    decorators: List[str] = None
    
    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []
        if self.bases is None:
            self.bases = []


@dataclass
class ImportInfo:
    """Information extracted from an import statement."""
    module: str
    names: List[str]
    alias: Optional[str] = None
    is_from_import: bool = False
    start_line: int = 0


class BaseExtractor(ABC):
    """
    Abstract base class for language-specific AST extractors.
    
    Each language implementation must provide methods to extract:
    - Functions (with signatures, docstrings)
    - Classes (with methods, inheritance)
    - Imports (modules and symbols)
    - Docstrings and comments
    """
    
    def __init__(self, tree: Tree, source: bytes):
        """
        Initialize extractor with parsed tree.
        
        Args:
            tree: Tree-sitter Tree object
            source: Original source code as bytes
        """
        self.tree = tree
        self.source = source
        self.root = tree.root_node
    
    @abstractmethod
    def extract_functions(self) -> List[FunctionInfo]:
        """
        Extract all function definitions.
        
        Returns:
            List of FunctionInfo objects
        """
        pass
    
    @abstractmethod
    def extract_classes(self) -> List[ClassInfo]:
        """
        Extract all class definitions.
        
        Returns:
            List of ClassInfo objects
        """
        pass
    
    @abstractmethod
    def extract_imports(self) -> List[ImportInfo]:
        """
        Extract all import statements.
        
        Returns:
            List of ImportInfo objects
        """
        pass
    
    def get_node_text(self, node: Node) -> str:
        """
        Get text content of a node.
        
        Args:
            node: Tree-sitter Node
            
        Returns:
            Node text as string
        """
        if node is None:
            return ""
        return self.source[node.start_byte:node.end_byte].decode('utf-8')
    
    def get_docstring(self, node: Node) -> Optional[str]:
        """
        Extract docstring from a function or class node.
        
        Args:
            node: Function or class node
            
        Returns:
            Docstring text or None
        """
        # Default implementation - override in language-specific extractors
        return None
    
    def find_child_by_type(self, node: Node, node_type: str) -> Optional[Node]:
        """
        Find first child of given type.
        
        Args:
            node: Parent node
            node_type: Type to search for
            
        Returns:
            First matching child or None
        """
        for child in node.children:
            if child.type == node_type:
                return child
        return None
    
    def find_children_by_type(self, node: Node, node_type: str) -> List[Node]:
        """
        Find all children of given type.
        
        Args:
            node: Parent node
            node_type: Type to search for
            
        Returns:
            List of matching children
        """
        return [child for child in node.children if child.type == node_type]


__all__ = [
    'BaseExtractor',
    'FunctionInfo',
    'ClassInfo',
    'ImportInfo',
]
