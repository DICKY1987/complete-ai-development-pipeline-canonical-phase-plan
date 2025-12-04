"""
Tests for Python-specific AST extractor.
"""

# DOC_ID: DOC-TEST-SYNTAX-ANALYSIS-TEST-PYTHON-153

import pytest

from core.ast.languages.python import PythonExtractor
from core.ast.parser import ASTParser


class TestPythonExtractorFunctions:
    """Test function extraction."""

    def test_extract_simple_function(self):
        """Test extracting a simple function."""
        source = b"def hello():\n    return 'world'"
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        functions = extractor.extract_functions()
        assert len(functions) == 1
        assert functions[0].name == "hello"
        assert functions[0].params == []
        assert not functions[0].is_async

    def test_extract_function_with_params(self):
        """Test extracting function with parameters."""
        source = b"def greet(name, age):\n    pass"
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        functions = extractor.extract_functions()
        assert len(functions) == 1
        assert functions[0].params == ["name", "age"]

    def test_extract_function_with_defaults(self):
        """Test extracting function with default parameters."""
        source = b"def func(a, b=10, c='test'):\n    pass"
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        functions = extractor.extract_functions()
        assert len(functions) == 1
        assert "a" in functions[0].params
        assert "b" in functions[0].params
        assert "c" in functions[0].params

    def test_extract_function_with_docstring(self):
        """Test extracting function docstring."""
        source = b'''def documented():
    """This is a docstring."""
    pass'''
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        functions = extractor.extract_functions()
        assert len(functions) == 1
        assert "docstring" in functions[0].docstring.lower()

    def test_extract_async_function(self):
        """Test extracting async function."""
        source = b"async def async_func():\n    await something()"
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        functions = extractor.extract_functions()
        assert len(functions) == 1
        assert functions[0].name == "async_func"
        assert functions[0].is_async

    def test_extract_decorated_function(self):
        """Test extracting decorated function."""
        source = b"""@staticmethod
@property
def decorated():
    pass"""
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        functions = extractor.extract_functions()
        assert len(functions) == 1
        assert len(functions[0].decorators) == 2

    def test_extract_multiple_functions(self):
        """Test extracting multiple functions."""
        source = b"""def func1():
    pass

def func2():
    pass

def func3():
    pass"""
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        functions = extractor.extract_functions()
        assert len(functions) == 3
        assert [f.name for f in functions] == ["func1", "func2", "func3"]

    def test_extract_nested_functions(self):
        """Test extracting nested functions."""
        source = b"""def outer():
    def inner():
        pass
    return inner"""
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        functions = extractor.extract_functions()
        # Should extract both outer and inner
        assert len(functions) == 2
        names = [f.name for f in functions]
        assert "outer" in names
        assert "inner" in names


class TestPythonExtractorClasses:
    """Test class extraction."""

    def test_extract_simple_class(self):
        """Test extracting a simple class."""
        source = b"class MyClass:\n    pass"
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        classes = extractor.extract_classes()
        assert len(classes) == 1
        assert classes[0].name == "MyClass"
        assert classes[0].bases == []

    def test_extract_class_with_inheritance(self):
        """Test extracting class with base classes."""
        source = b"class Child(Parent, Mixin):\n    pass"
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        classes = extractor.extract_classes()
        assert len(classes) == 1
        assert classes[0].bases == ["Parent", "Mixin"]

    def test_extract_class_with_methods(self):
        """Test extracting class methods."""
        source = b"""class MyClass:
    def __init__(self):
        pass

    def method1(self):
        pass

    @property
    def method2(self):
        pass"""
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        classes = extractor.extract_classes()
        assert len(classes) == 1
        assert len(classes[0].methods) == 3
        assert "__init__" in classes[0].methods
        assert "method1" in classes[0].methods
        assert "method2" in classes[0].methods

    def test_extract_class_with_docstring(self):
        """Test extracting class docstring."""
        source = b'''class Documented:
    """This is a class docstring."""
    pass'''
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        classes = extractor.extract_classes()
        assert len(classes) == 1
        assert "class docstring" in classes[0].docstring.lower()

    def test_extract_decorated_class(self):
        """Test extracting decorated class."""
        source = b"""@dataclass
class Decorated:
    pass"""
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        classes = extractor.extract_classes()
        assert len(classes) == 1
        assert len(classes[0].decorators) == 1

    def test_extract_multiple_classes(self):
        """Test extracting multiple classes."""
        source = b"""class Class1:
    pass

class Class2:
    pass"""
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        classes = extractor.extract_classes()
        assert len(classes) == 2


class TestPythonExtractorImports:
    """Test import extraction."""

    def test_extract_simple_import(self):
        """Test extracting simple import."""
        source = b"import os"
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        imports = extractor.extract_imports()
        assert len(imports) == 1
        assert imports[0].module == "os"
        assert not imports[0].is_from_import

    def test_extract_from_import(self):
        """Test extracting from import."""
        source = b"from pathlib import Path"
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        imports = extractor.extract_imports()
        assert len(imports) >= 1
        import_info = imports[0]
        assert import_info.module == "pathlib"
        assert import_info.is_from_import

    def test_extract_import_with_alias(self):
        """Test extracting import with alias."""
        source = b"import numpy as np"
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        imports = extractor.extract_imports()
        assert len(imports) == 1
        assert imports[0].alias == "np"

    def test_extract_wildcard_import(self):
        """Test extracting wildcard import."""
        source = b"from module import *"
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        imports = extractor.extract_imports()
        assert len(imports) >= 1
        # Check that wildcard is captured
        assert any("*" in imp.names for imp in imports)

    def test_extract_multiple_imports(self):
        """Test extracting multiple imports."""
        source = b"""import os
import sys
from pathlib import Path"""
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        imports = extractor.extract_imports()
        assert len(imports) >= 3


class TestPythonExtractorIntegration:
    """Integration tests with real code."""

    def test_extract_from_real_code(self):
        """Test extraction from realistic Python code."""
        source = b'''"""Module docstring."""

import os
from pathlib import Path

class DataProcessor:
    """Process data."""

    def __init__(self, path):
        self.path = path

    def process(self):
        """Process the data."""
        return self._helper()

    def _helper(self):
        return 42

def utility_function(x, y=10):
    """A utility function."""
    return x + y

async def async_handler():
    await something()
'''
        parser = ASTParser("python")
        tree = parser.parse_string(source)
        extractor = PythonExtractor(tree, source)

        # Test all extractors work together
        functions = extractor.extract_functions()
        classes = extractor.extract_classes()
        imports = extractor.extract_imports()

        # Verify results
        assert len(functions) >= 2  # utility_function, async_handler (+ methods)
        assert len(classes) == 1
        assert classes[0].name == "DataProcessor"
        assert len(imports) >= 2
