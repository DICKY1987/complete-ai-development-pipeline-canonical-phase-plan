"""
Test AST parser functionality.
"""
# DOC_ID: DOC-TESTS-AST-TEST-PARSER-210

import pytest
from pathlib import Path
import tempfile

from core.ast.parser import ASTParser, create_parser


def test_parser_initialization():
    """Test parser can be initialized."""
    parser = ASTParser()
    assert parser is not None
    assert 'python' in parser.supported_languages()


def test_create_parser_factory():
    """Test parser factory function."""
    parser = create_parser()
    assert isinstance(parser, ASTParser)


def test_supported_languages():
    """Test supported languages list."""
    languages = ASTParser.supported_languages()
    assert 'python' in languages
    assert 'javascript' in languages
    assert 'typescript' in languages


def test_supported_extensions():
    """Test supported file extensions."""
    extensions = ASTParser.supported_extensions()
    assert '.py' in extensions
    assert '.js' in extensions
    assert '.ts' in extensions


def test_parse_simple_python():
    """Test parsing simple Python code."""
    parser = ASTParser()
    
    code = """
def hello(name):
    return f"Hello, {name}!"
"""
    
    tree = parser.parse_string(code, 'python')
    assert tree is not None
    assert tree.root_node is not None
    assert parser.current_language == 'python'


def test_parse_python_with_class():
    """Test parsing Python code with class."""
    parser = ASTParser()
    
    code = """
class Greeting:
    def __init__(self, message):
        self.message = message
    
    def greet(self, name):
        return f"{self.message}, {name}!"
"""
    
    tree = parser.parse_string(code, 'python')
    assert tree is not None
    assert tree.root_node.type == 'module'


def test_parse_python_with_imports():
    """Test parsing Python code with imports."""
    parser = ASTParser()
    
    code = """
import os
from pathlib import Path
from typing import Dict, List

def process(data: Dict) -> List:
    return list(data.values())
"""
    
    tree = parser.parse_string(code, 'python')
    assert tree is not None


def test_parse_file(tmp_path):
    """Test parsing a Python file."""
    parser = ASTParser()
    
    # Create temporary Python file
    py_file = tmp_path / "test.py"
    py_file.write_text("""
def add(a, b):
    return a + b
""")
    
    tree = parser.parse_file(py_file)
    assert tree is not None


def test_parse_file_autodetect_language(tmp_path):
    """Test language auto-detection from file extension."""
    parser = ASTParser()
    
    py_file = tmp_path / "test.py"
    py_file.write_text("def test(): pass")
    
    tree = parser.parse_file(py_file)
    assert tree is not None
    assert parser.current_language == 'python'


def test_parse_nonexistent_file():
    """Test parsing nonexistent file raises error."""
    parser = ASTParser()
    
    with pytest.raises(FileNotFoundError):
        parser.parse_file(Path("/nonexistent/file.py"))


def test_parse_unsupported_language():
    """Test parsing unsupported language raises error."""
    parser = ASTParser()
    
    with pytest.raises(ValueError):
        parser.parse_string("code", "unsupported")


def test_get_language():
    """Test getting language object."""
    parser = ASTParser()
    
    lang = parser.get_language('python')
    assert lang is not None


def test_get_unsupported_language():
    """Test getting unsupported language raises error."""
    parser = ASTParser()
    
    with pytest.raises(ValueError):
        parser.get_language('unsupported')


def test_parse_async_function():
    """Test parsing async function."""
    parser = ASTParser()
    
    code = """
async def fetch_data(url):
    return await request(url)
"""
    
    tree = parser.parse_string(code, 'python')
    assert tree is not None


def test_parse_decorated_function():
    """Test parsing decorated function."""
    parser = ASTParser()
    
    code = """
@decorator
@another_decorator
def my_function(x):
    return x * 2
"""
    
    tree = parser.parse_string(code, 'python')
    assert tree is not None


def test_parse_multiple_files(tmp_path):
    """Test parsing multiple files."""
    parser = ASTParser()
    
    # Create multiple files
    files = []
    for i in range(3):
        py_file = tmp_path / f"test_{i}.py"
        py_file.write_text(f"def func_{i}(): pass")
        files.append(py_file)
    
    # Parse all files
    trees = [parser.parse_file(f) for f in files]
    assert len(trees) == 3
    assert all(t is not None for t in trees)
