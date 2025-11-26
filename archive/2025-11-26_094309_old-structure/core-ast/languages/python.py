"""
Python-specific AST extractor.

Implements BaseExtractor for Python using Tree-sitter Python grammar.
"""

from typing import List, Optional
from tree_sitter import Node, Tree

from modules.core_ast.m010000_extractors import (
    BaseExtractor,
    FunctionInfo,
    ClassInfo,
    ImportInfo,
)


class PythonExtractor(BaseExtractor):
    """
    Python-specific AST extractor.
    
    Extracts:
    - Functions (def, async def) with signatures and docstrings
    - Classes with methods and inheritance
    - Imports (import, from...import)
    - Decorators (@property, @staticmethod, etc.)
    """
    
    def extract_functions(self) -> List[FunctionInfo]:
        """
        Extract all function definitions from Python AST.
        
        Returns:
            List of FunctionInfo objects
        """
        functions = []
        
        def visit(node: Node):
            if node.type == 'function_definition':
                func_info = self._extract_function_info(node)
                if func_info:
                    functions.append(func_info)
            
            for child in node.children:
                visit(child)
        
        visit(self.root)
        return functions
    
    def _extract_function_info(self, node: Node) -> Optional[FunctionInfo]:
        """Extract information from a function_definition node."""
        # Get function name
        name_node = self.find_child_by_type(node, 'identifier')
        if not name_node:
            return None
        
        name = self.get_node_text(name_node)
        
        # Get parameters
        params = self._extract_parameters(node)
        
        # Get return type (if annotated)
        return_type = self._extract_return_type(node)
        
        # Get docstring
        docstring = self._extract_function_docstring(node)
        
        # Get decorators
        decorators = self._extract_decorators(node)
        
        # Check if async
        is_async = node.children[0].type == 'async' if node.children else False
        
        return FunctionInfo(
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            params=params,
            return_type=return_type,
            docstring=docstring,
            decorators=decorators,
            is_async=is_async,
        )
    
    def _extract_parameters(self, func_node: Node) -> List[str]:
        """Extract parameter names from function."""
        params = []
        params_node = self.find_child_by_type(func_node, 'parameters')
        
        if params_node:
            for child in params_node.children:
                if child.type == 'identifier':
                    params.append(self.get_node_text(child))
                elif child.type == 'typed_parameter':
                    # Get parameter name from typed parameter
                    ident = self.find_child_by_type(child, 'identifier')
                    if ident:
                        params.append(self.get_node_text(ident))
                elif child.type == 'default_parameter':
                    # Get parameter name from default parameter
                    ident = self.find_child_by_type(child, 'identifier')
                    if ident:
                        params.append(self.get_node_text(ident))
        
        return params
    
    def _extract_return_type(self, func_node: Node) -> Optional[str]:
        """Extract return type annotation if present."""
        type_node = self.find_child_by_type(func_node, 'type')
        if type_node:
            return self.get_node_text(type_node)
        return None
    
    def _extract_function_docstring(self, func_node: Node) -> Optional[str]:
        """Extract docstring from function body."""
        body = self.find_child_by_type(func_node, 'block')
        if not body or not body.children:
            return None
        
        # First statement might be a docstring
        first_stmt = body.children[0]
        if first_stmt.type == 'expression_statement':
            expr = first_stmt.children[0] if first_stmt.children else None
            if expr and expr.type == 'string':
                # Remove quotes
                text = self.get_node_text(expr)
                return text.strip('"\'')
        
        return None
    
    def _extract_decorators(self, node: Node) -> List[str]:
        """Extract decorator names from decorated_definition."""
        decorators = []
        parent = node.parent
        
        if parent and parent.type == 'decorated_definition':
            for child in parent.children:
                if child.type == 'decorator':
                    # Get decorator name (skip the @ symbol)
                    dec_text = self.get_node_text(child)
                    decorators.append(dec_text.lstrip('@'))
        
        return decorators
    
    def extract_classes(self) -> List[ClassInfo]:
        """
        Extract all class definitions from Python AST.
        
        Returns:
            List of ClassInfo objects
        """
        classes = []
        
        def visit(node: Node):
            if node.type == 'class_definition':
                class_info = self._extract_class_info(node)
                if class_info:
                    classes.append(class_info)
            
            for child in node.children:
                visit(child)
        
        visit(self.root)
        return classes
    
    def _extract_class_info(self, node: Node) -> Optional[ClassInfo]:
        """Extract information from a class_definition node."""
        # Get class name
        name_node = self.find_child_by_type(node, 'identifier')
        if not name_node:
            return None
        
        name = self.get_node_text(name_node)
        
        # Get base classes
        bases = self._extract_base_classes(node)
        
        # Get methods
        methods = self._extract_methods(node)
        
        # Get docstring
        docstring = self._extract_class_docstring(node)
        
        # Get decorators
        decorators = self._extract_decorators(node)
        
        return ClassInfo(
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            bases=bases,
            methods=methods,
            docstring=docstring,
            decorators=decorators,
        )
    
    def _extract_base_classes(self, class_node: Node) -> List[str]:
        """Extract base class names."""
        bases = []
        arg_list = self.find_child_by_type(class_node, 'argument_list')
        
        if arg_list:
            for child in arg_list.children:
                if child.type == 'identifier':
                    bases.append(self.get_node_text(child))
                elif child.type == 'attribute':
                    bases.append(self.get_node_text(child))
        
        return bases
    
    def _extract_methods(self, class_node: Node) -> List[str]:
        """Extract method names from class body."""
        methods = []
        body = self.find_child_by_type(class_node, 'block')
        
        if body:
            for child in body.children:
                if child.type == 'function_definition':
                    name_node = self.find_child_by_type(child, 'identifier')
                    if name_node:
                        methods.append(self.get_node_text(name_node))
                elif child.type == 'decorated_definition':
                    # Method with decorators
                    func = self.find_child_by_type(child, 'function_definition')
                    if func:
                        name_node = self.find_child_by_type(func, 'identifier')
                        if name_node:
                            methods.append(self.get_node_text(name_node))
        
        return methods
    
    def _extract_class_docstring(self, class_node: Node) -> Optional[str]:
        """Extract docstring from class body."""
        body = self.find_child_by_type(class_node, 'block')
        if not body or not body.children:
            return None
        
        # First statement might be a docstring
        first_stmt = body.children[0]
        if first_stmt.type == 'expression_statement':
            expr = first_stmt.children[0] if first_stmt.children else None
            if expr and expr.type == 'string':
                text = self.get_node_text(expr)
                return text.strip('"\'')
        
        return None
    
    def extract_imports(self) -> List[ImportInfo]:
        """
        Extract all import statements from Python AST.
        
        Returns:
            List of ImportInfo objects
        """
        imports = []
        
        def visit(node: Node):
            if node.type == 'import_statement':
                import_info = self._extract_import_statement(node)
                if import_info:
                    imports.append(import_info)
            elif node.type == 'import_from_statement':
                import_infos = self._extract_from_import_statement(node)
                imports.extend(import_infos)
            
            for child in node.children:
                visit(child)
        
        visit(self.root)
        return imports
    
    def _extract_import_statement(self, node: Node) -> Optional[ImportInfo]:
        """Extract from 'import module' statement."""
        # Find dotted_name or aliased_import
        for child in node.children:
            if child.type == 'dotted_name':
                module = self.get_node_text(child)
                return ImportInfo(
                    module=module,
                    names=[module],
                    is_from_import=False,
                    start_line=node.start_point[0] + 1,
                )
            elif child.type == 'aliased_import':
                name_node = self.find_child_by_type(child, 'dotted_name')
                alias_node = self.find_child_by_type(child, 'identifier')
                if name_node:
                    module = self.get_node_text(name_node)
                    alias = self.get_node_text(alias_node) if alias_node else None
                    return ImportInfo(
                        module=module,
                        names=[module],
                        alias=alias,
                        is_from_import=False,
                        start_line=node.start_point[0] + 1,
                    )
        
        return None
    
    def _extract_from_import_statement(self, node: Node) -> List[ImportInfo]:
        """Extract from 'from module import names' statement."""
        imports = []
        
        # Find module name
        module_node = self.find_child_by_type(node, 'dotted_name')
        if not module_node:
            return imports
        
        module = self.get_node_text(module_node)
        
        # Find imported names
        for child in node.children:
            if child.type == 'dotted_name' and child != module_node:
                name = self.get_node_text(child)
                imports.append(ImportInfo(
                    module=module,
                    names=[name],
                    is_from_import=True,
                    start_line=node.start_point[0] + 1,
                ))
            elif child.type == 'aliased_import':
                name_node = self.find_child_by_type(child, 'dotted_name')
                alias_node = child.children[-1] if len(child.children) > 2 else None
                if name_node:
                    name = self.get_node_text(name_node)
                    alias = self.get_node_text(alias_node) if alias_node and alias_node.type == 'identifier' else None
                    imports.append(ImportInfo(
                        module=module,
                        names=[name],
                        alias=alias,
                        is_from_import=True,
                        start_line=node.start_point[0] + 1,
                    ))
            elif child.type == 'wildcard_import':
                imports.append(ImportInfo(
                    module=module,
                    names=['*'],
                    is_from_import=True,
                    start_line=node.start_point[0] + 1,
                ))
        
        return imports


__all__ = ['PythonExtractor']
