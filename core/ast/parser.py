"""
Tree-sitter based AST parser for multiple languages.

Provides unified parsing interface for Python, JavaScript, and TypeScript.
"""
# DOC_ID: DOC-CORE-AST-PARSER-200

from pathlib import Path
from typing import Optional, Dict, Any
from tree_sitter import Language, Parser, Tree
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript


class ASTParser:
    """
    Multi-language AST parser using tree-sitter.
    
    Supports:
    - Python (.py)
    - JavaScript (.js)
    - TypeScript (.ts, .tsx)
    """
    
    _language_cache: Dict[str, Language] = {}
    
    def __init__(self):
        """Initialize parser with language support."""
        self._parser = Parser()
        self._current_language = None
        self._initialize_languages()
    
    def _initialize_languages(self):
        """Load and cache tree-sitter languages."""
        if 'python' not in self._language_cache:
            self._language_cache['python'] = Language(tspython.language())
        if 'javascript' not in self._language_cache:
            self._language_cache['javascript'] = Language(tsjavascript.language())
        if 'typescript' not in self._language_cache:
            self._language_cache['typescript'] = Language(tsjavascript.language())
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """
        Detect language from file extension.
        
        Args:
            file_path: Path to source file
            
        Returns:
            Language name or None if unsupported
        """
        ext = file_path.suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
        }
        return language_map.get(ext)
    
    def parse_file(self, file_path: Path, language: Optional[str] = None) -> Optional[Tree]:
        """
        Parse a source file into an AST.
        
        Args:
            file_path: Path to source file
            language: Optional language override (auto-detected from extension)
            
        Returns:
            Tree-sitter Tree object or None if parsing failed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Detect language if not provided
        if language is None:
            language = self._detect_language(file_path)
            if language is None:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Set parser language
        if language not in self._language_cache:
            raise ValueError(f"Unsupported language: {language}")
        
        self._parser.language = self._language_cache[language]
        self._current_language = language
        
        # Read and parse file
        try:
            with open(file_path, 'rb') as f:
                source = f.read()
            return self._parser.parse(source)
        except Exception as e:
            raise RuntimeError(f"Failed to parse {file_path}: {e}")
    
    def parse_string(self, source: str, language: str) -> Optional[Tree]:
        """
        Parse source code string into an AST.
        
        Args:
            source: Source code string
            language: Language name (python, javascript, typescript)
            
        Returns:
            Tree-sitter Tree object or None if parsing failed
        """
        if language not in self._language_cache:
            raise ValueError(f"Unsupported language: {language}")
        
        self._parser.language = self._language_cache[language]
        self._current_language = language
        
        source_bytes = source.encode('utf-8')
        return self._parser.parse(source_bytes)
    
    def get_language(self, name: str) -> Language:
        """
        Get cached language object.
        
        Args:
            name: Language name
            
        Returns:
            Tree-sitter Language object
        """
        if name not in self._language_cache:
            raise ValueError(f"Language not loaded: {name}")
        return self._language_cache[name]
    
    @property
    def current_language(self) -> Optional[str]:
        """Get currently active language."""
        return self._current_language
    
    @staticmethod
    def supported_languages() -> list:
        """Get list of supported languages."""
        return ['python', 'javascript', 'typescript']
    
    @staticmethod
    def supported_extensions() -> list:
        """Get list of supported file extensions."""
        return ['.py', '.js', '.jsx', '.ts', '.tsx']


def create_parser() -> ASTParser:
    """
    Factory function to create a new parser instance.
    
    Returns:
        Configured ASTParser
    """
    return ASTParser()


__all__ = ['ASTParser', 'create_parser']
