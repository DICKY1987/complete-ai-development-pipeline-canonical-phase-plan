"""
Tests for AST parser core functionality.
"""
# DOC_ID: DOC-TEST-SYNTAX-ANALYSIS-TEST-PARSER-152

import pytest
from pathlib import Path
from core.ast.parser import ASTParser


class TestASTParserInit:
    """Test parser initialization."""
    
    def test_init_python(self):
        """Test Python parser initialization."""
        parser = ASTParser("python")
        assert parser.language_name == "python"
        assert parser.parser is not None
    
    def test_init_javascript(self):
        """Test JavaScript parser initialization."""
        parser = ASTParser("javascript")
        assert parser.language_name == "javascript"
    
    def test_init_typescript(self):
        """Test TypeScript parser initialization."""
        parser = ASTParser("typescript")
        assert parser.language_name == "typescript"
    
    def test_init_unsupported_language(self):
        """Test initialization with unsupported language."""
        with pytest.raises(ValueError, match="Unsupported language"):
            ASTParser("ruby")
    
    def test_init_case_insensitive(self):
        """Test language name is case-insensitive."""
        parser = ASTParser("PYTHON")
        assert parser.language_name == "python"


class TestASTParserString:
    """Test parsing from strings."""
    
    def test_parse_simple_python(self):
        """Test parsing simple Python code."""
        parser = ASTParser("python")
        source = "def hello():\n    return 'world'"
        tree = parser.parse_string(source)
        
        assert tree is not None
        assert tree.root_node is not None
        assert not parser.has_errors(tree)
    
    def test_parse_bytes(self):
        """Test parsing from bytes."""
        parser = ASTParser("python")
        source = b"x = 1"
        tree = parser.parse_string(source)
        
        assert tree is not None
        assert not parser.has_errors(tree)
    
    def test_parse_unicode(self):
        """Test parsing Unicode characters."""
        parser = ASTParser("python")
        source = "# Comment with émojis 🎉\nx = 'café'"
        tree = parser.parse_string(source)
        
        assert not parser.has_errors(tree)
    
    def test_parse_syntax_error(self):
        """Test parsing code with syntax errors."""
        parser = ASTParser("python")
        source = "def broken(\n    pass"  # Missing closing paren
        tree = parser.parse_string(source)
        
        assert parser.has_errors(tree)
        errors = parser.get_error_nodes(tree)
        assert len(errors) > 0


class TestASTParserFile:
    """Test parsing from files."""
    
    def test_parse_existing_file(self, tmp_path):
        """Test parsing an existing Python file."""
        # Create temp file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test():\n    pass")
        
        parser = ASTParser("python")
        tree = parser.parse_file(test_file)
        
        assert tree is not None
        assert not parser.has_errors(tree)
    
    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist."""
        parser = ASTParser("python")
        
        with pytest.raises(FileNotFoundError):
            parser.parse_file("nonexistent.py")
    
    def test_parse_real_file(self):
        """Test parsing a real file from the codebase."""
        parser = ASTParser("python")
        
        # Parse this test file itself
        test_file = Path(__file__)
        tree = parser.parse_file(test_file)
        
        assert tree is not None
        # Should have some function definitions
        root = tree.root_node
        assert root.type == "module"


class TestASTParserErrors:
    """Test error detection and handling."""
    
    def test_has_errors_false(self):
        """Test has_errors returns False for valid code."""
        parser = ASTParser("python")
        tree = parser.parse_string("x = 1")
        
        assert not parser.has_errors(tree)
    
    def test_has_errors_true(self):
        """Test has_errors returns True for invalid code."""
        parser = ASTParser("python")
        tree = parser.parse_string("def broken(")
        
        assert parser.has_errors(tree)
    
    def test_get_error_nodes(self):
        """Test extracting error node information."""
        parser = ASTParser("python")
        tree = parser.parse_string("x = ")  # Incomplete assignment
        
        errors = parser.get_error_nodes(tree)
        assert len(errors) > 0
        
        # Check error structure
        error = errors[0]
        assert 'type' in error
        assert 'start_point' in error
        assert 'end_point' in error
    
    def test_get_error_nodes_empty(self):
        """Test get_error_nodes returns empty list for valid code."""
        parser = ASTParser("python")
        tree = parser.parse_string("x = 1")
        
        errors = parser.get_error_nodes(tree)
        assert len(errors) == 0


class TestASTParserComplexCode:
    """Test parsing complex code structures."""
    
    def test_parse_class(self):
        """Test parsing Python class."""
        parser = ASTParser("python")
        source = """
class MyClass:
    def __init__(self):
        pass
    
    def method(self):
        return 42
"""
        tree = parser.parse_string(source)
        assert not parser.has_errors(tree)
    
    def test_parse_decorators(self):
        """Test parsing decorated functions."""
        parser = ASTParser("python")
        source = """
@property
@staticmethod
def decorated():
    pass
"""
        tree = parser.parse_string(source)
        assert not parser.has_errors(tree)
    
    def test_parse_async(self):
        """Test parsing async functions."""
        parser = ASTParser("python")
        source = """
async def async_func():
    await something()
"""
        tree = parser.parse_string(source)
        assert not parser.has_errors(tree)
    
    def test_parse_imports(self):
        """Test parsing various import statements."""
        parser = ASTParser("python")
        source = """
import os
from pathlib import Path
from typing import List, Optional
import numpy as np
"""
        tree = parser.parse_string(source)
        assert not parser.has_errors(tree)
