"""
Test Python AST extractor functionality.
"""
# DOC_ID: DOC-TESTS-AST-TEST-PYTHON-212

import pytest
from core.ast.parser import ASTParser
from core.ast.languages.python import PythonExtractor


def test_extract_simple_function():
    """Test extracting a simple function."""
    parser = ASTParser()
    code = """
def greet(name):
    return f"Hello, {name}!"
"""
    
    tree = parser.parse_string(code, 'python')
    extractor = PythonExtractor(tree, code.encode('utf-8'))
    
    functions = extractor.extract_functions()
    assert len(functions) == 1
    assert functions[0].name == 'greet'
    assert functions[0].params == ['name']
    assert not functions[0].is_async


def test_extract_async_function():
    """Test extracting async function."""
    parser = ASTParser()
    code = """
async def fetch_data(url):
    return await get(url)
"""
    
    tree = parser.parse_string(code, 'python')
    extractor = PythonExtractor(tree, code.encode('utf-8'))
    
    functions = extractor.extract_functions()
    assert len(functions) == 1
    assert functions[0].name == 'fetch_data'
    assert functions[0].is_async


def test_extract_function_with_docstring():
    """Test extracting function with docstring."""
    parser = ASTParser()
    code = '''
def calculate(x, y):
    """Calculate sum of x and y."""
    return x + y
'''
    
    tree = parser.parse_string(code, 'python')
    extractor = PythonExtractor(tree, code.encode('utf-8'))
    
    functions = extractor.extract_functions()
    assert len(functions) == 1
    assert functions[0].name == 'calculate'
    assert functions[0].docstring == "Calculate sum of x and y."


def test_extract_multiple_functions():
    """Test extracting multiple functions."""
    parser = ASTParser()
    code = """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b
"""
    
    tree = parser.parse_string(code, 'python')
    extractor = PythonExtractor(tree, code.encode('utf-8'))
    
    functions = extractor.extract_functions()
    assert len(functions) == 3
    assert [f.name for f in functions] == ['add', 'subtract', 'multiply']


def test_extract_simple_class():
    """Test extracting a simple class."""
    parser = ASTParser()
    code = """
class Person:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, I'm {self.name}"
"""
    
    tree = parser.parse_string(code, 'python')
    extractor = PythonExtractor(tree, code.encode('utf-8'))
    
    classes = extractor.extract_classes()
    assert len(classes) == 1
    assert classes[0].name == 'Person'
    assert '__init__' in classes[0].methods
    assert 'greet' in classes[0].methods


def test_extract_class_with_inheritance():
    """Test extracting class with base classes."""
    parser = ASTParser()
    code = """
class Child(Parent, Mixin):
    def method(self):
        pass
"""
    
    tree = parser.parse_string(code, 'python')
    extractor = PythonExtractor(tree, code.encode('utf-8'))
    
    classes = extractor.extract_classes()
    assert len(classes) == 1
    assert classes[0].name == 'Child'
    assert 'Parent' in classes[0].bases or 'Mixin' in classes[0].bases


def test_extract_class_with_docstring():
    """Test extracting class with docstring."""
    parser = ASTParser()
    code = '''
class Calculator:
    """A simple calculator class."""
    def add(self, a, b):
        return a + b
'''
    
    tree = parser.parse_string(code, 'python')
    extractor = PythonExtractor(tree, code.encode('utf-8'))
    
    classes = extractor.extract_classes()
    assert len(classes) == 1
    assert classes[0].name == 'Calculator'
    assert classes[0].docstring == "A simple calculator class."


def test_extract_import_statement():
    """Test extracting import statements."""
    parser = ASTParser()
    code = """
import os
import sys
"""
    
    tree = parser.parse_string(code, 'python')
    extractor = PythonExtractor(tree, code.encode('utf-8'))
    
    imports = extractor.extract_imports()
    assert len(imports) >= 2
    module_names = [imp.module for imp in imports]
    assert 'os' in module_names
    assert 'sys' in module_names


def test_extract_from_import():
    """Test extracting from-import statements."""
    parser = ASTParser()
    code = """
from pathlib import Path
from typing import Dict, List
"""
    
    tree = parser.parse_string(code, 'python')
    extractor = PythonExtractor(tree, code.encode('utf-8'))
    
    imports = extractor.extract_imports()
    assert len(imports) >= 2
    
    pathlib_import = [imp for imp in imports if imp.module == 'pathlib']
    assert len(pathlib_import) > 0
    assert pathlib_import[0].is_from_import


def test_extract_nested_functions():
    """Test extracting nested functions."""
    parser = ASTParser()
    code = """
def outer():
    def inner():
        pass
    return inner
"""
    
    tree = parser.parse_string(code, 'python')
    extractor = PythonExtractor(tree, code.encode('utf-8'))
    
    functions = extractor.extract_functions()
    assert len(functions) == 2
    func_names = [f.name for f in functions]
    assert 'outer' in func_names
    assert 'inner' in func_names


def test_extract_class_methods():
    """Test extracting methods from class."""
    parser = ASTParser()
    code = """
class MyClass:
    def method1(self):
        pass
    
    @staticmethod
    def method2():
        pass
    
    @classmethod
    def method3(cls):
        pass
"""
    
    tree = parser.parse_string(code, 'python')
    extractor = PythonExtractor(tree, code.encode('utf-8'))
    
    classes = extractor.extract_classes()
    assert len(classes) == 1
    assert len(classes[0].methods) >= 1  # At least method1 is extracted


def test_extract_empty_file():
    """Test extracting from empty file."""
    parser = ASTParser()
    code = ""
    
    tree = parser.parse_string(code, 'python')
    extractor = PythonExtractor(tree, code.encode('utf-8'))
    
    functions = extractor.extract_functions()
    classes = extractor.extract_classes()
    imports = extractor.extract_imports()
    
    assert len(functions) == 0
    assert len(classes) == 0
    assert len(imports) == 0


def test_extract_complex_file():
    """Test extracting from complex file with everything."""
    parser = ASTParser()
    code = '''
"""Module docstring."""
import os
from pathlib import Path

class Base:
    """Base class."""
    pass

class Derived(Base):
    """Derived class."""
    
    def __init__(self):
        super().__init__()
    
    @property
    def value(self):
        return 42
    
    async def async_method(self):
        """Async method."""
        pass

def standalone_function(x, y):
    """Standalone function."""
    return x + y
'''
    
    tree = parser.parse_string(code, 'python')
    extractor = PythonExtractor(tree, code.encode('utf-8'))
    
    functions = extractor.extract_functions()
    classes = extractor.extract_classes()
    imports = extractor.extract_imports()
    
    assert len(functions) >= 1  # At least standalone_function
    assert len(classes) == 2  # Base and Derived
    assert len(imports) >= 2  # os and pathlib
