"""
Python-specific AST extraction using tree-sitter.

Extracts functions, classes, imports, and docstrings from Python source code.
"""
# DOC_ID: DOC-CORE-AST-LANGUAGES-PYTHON-202

from typing import List, Optional
from tree_sitter import Node, Tree
from ..extractors import BaseExtractor, FunctionInfo, ClassInfo, ImportInfo


class PythonExtractor(BaseExtractor):
    """Extract AST information from Python source code."""
    
    def extract_functions(self) -> List[FunctionInfo]:
        """
        Extract all function definitions from Python code.
        
        Returns:
            List of FunctionInfo objects
        """
        functions = []
        self._extract_functions_recursive(self.root, functions)
        return functions
    
    def _extract_functions_recursive(self, node: Node, functions: List[FunctionInfo]):
        """Recursively extract functions from node tree."""
        if node.type == 'function_definition':
            func_info = self._parse_function(node)
            if func_info:
                functions.append(func_info)
        
        for child in node.children:
            self._extract_functions_recursive(child, functions)
    
    def _parse_function(self, node: Node) -> Optional[FunctionInfo]:
        """
        Parse a function_definition node.
        
        Args:
            node: function_definition node
            
        Returns:
            FunctionInfo or None
        """
        # Get function name
        name_node = self.find_child_by_type(node, 'identifier')
        if not name_node:
            return None
        name = self.get_node_text(name_node)
        
        # Check for async
        is_async = False
        if node.children and node.children[0].type == 'async':
            is_async = True
        
        # Get parameters
        params = self._extract_parameters(node)
        
        # Get return type annotation
        return_type = self._extract_return_type(node)
        
        # Get decorators
        decorators = self._extract_decorators(node)
        
        # Get docstring
        docstring = self._extract_function_docstring(node)
        
        return FunctionInfo(
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            params=params,
            return_type=return_type,
            docstring=docstring,
            decorators=decorators,
            is_async=is_async
        )
    
    def _extract_parameters(self, func_node: Node) -> List[str]:
        """Extract parameter names from function."""
        params = []
        params_node = self.find_child_by_type(func_node, 'parameters')
        if not params_node:
            return params
        
        for child in params_node.children:
            if child.type == 'identifier':
                params.append(self.get_node_text(child))
            elif child.type == 'typed_parameter':
                # Get name from typed parameter
                name_node = self.find_child_by_type(child, 'identifier')
                if name_node:
                    params.append(self.get_node_text(name_node))
            elif child.type == 'default_parameter':
                # Get name from default parameter
                name_node = self.find_child_by_type(child, 'identifier')
                if name_node:
                    params.append(self.get_node_text(name_node))
        
        return params
    
    def _extract_return_type(self, func_node: Node) -> Optional[str]:
        """Extract return type annotation."""
        type_node = self.find_child_by_type(func_node, 'type')
        if type_node:
            return self.get_node_text(type_node)
        return None
    
    def _extract_decorators(self, func_node: Node) -> List[str]:
        """Extract decorator names."""
        decorators = []
        # Check previous siblings for decorators
        parent = func_node.parent
        if parent:
            for child in parent.children:
                if child.type == 'decorator':
                    dec_text = self.get_node_text(child).lstrip('@').strip()
                    decorators.append(dec_text)
        return decorators
    
    def _extract_function_docstring(self, func_node: Node) -> Optional[str]:
        """Extract docstring from function body."""
        body_node = self.find_child_by_type(func_node, 'block')
        if not body_node or not body_node.children:
            return None
        
        # First statement might be a docstring
        first_stmt = body_node.children[0]
        if first_stmt.type == 'expression_statement':
            expr = self.find_child_by_type(first_stmt, 'string')
            if expr:
                docstring = self.get_node_text(expr)
                # Remove quotes
                docstring = docstring.strip('"""').strip("'''").strip('"').strip("'")
                return docstring.strip()
        
        return None
    
    def extract_classes(self) -> List[ClassInfo]:
        """
        Extract all class definitions from Python code.
        
        Returns:
            List of ClassInfo objects
        """
        classes = []
        self._extract_classes_recursive(self.root, classes)
        return classes
    
    def _extract_classes_recursive(self, node: Node, classes: List[ClassInfo]):
        """Recursively extract classes from node tree."""
        if node.type == 'class_definition':
            class_info = self._parse_class(node)
            if class_info:
                classes.append(class_info)
        
        for child in node.children:
            self._extract_classes_recursive(child, classes)
    
    def _parse_class(self, node: Node) -> Optional[ClassInfo]:
        """
        Parse a class_definition node.
        
        Args:
            node: class_definition node
            
        Returns:
            ClassInfo or None
        """
        # Get class name
        name_node = self.find_child_by_type(node, 'identifier')
        if not name_node:
            return None
        name = self.get_node_text(name_node)
        
        # Get base classes
        bases = self._extract_base_classes(node)
        
        # Get method names
        methods = self._extract_method_names(node)
        
        # Get decorators
        decorators = self._extract_class_decorators(node)
        
        # Get docstring
        docstring = self._extract_class_docstring(node)
        
        return ClassInfo(
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            bases=bases,
            methods=methods,
            docstring=docstring,
            decorators=decorators
        )
    
    def _extract_base_classes(self, class_node: Node) -> List[str]:
        """Extract base class names."""
        bases = []
        arg_list = self.find_child_by_type(class_node, 'argument_list')
        if arg_list:
            for child in arg_list.children:
                if child.type == 'identifier':
                    bases.append(self.get_node_text(child))
        return bases
    
    def _extract_method_names(self, class_node: Node) -> List[str]:
        """Extract method names from class body."""
        methods = []
        body_node = self.find_child_by_type(class_node, 'block')
        if body_node:
            for child in body_node.children:
                if child.type == 'function_definition':
                    name_node = self.find_child_by_type(child, 'identifier')
                    if name_node:
                        methods.append(self.get_node_text(name_node))
        return methods
    
    def _extract_class_decorators(self, class_node: Node) -> List[str]:
        """Extract class decorator names."""
        decorators = []
        parent = class_node.parent
        if parent:
            for child in parent.children:
                if child.type == 'decorator':
                    dec_text = self.get_node_text(child).lstrip('@').strip()
                    decorators.append(dec_text)
        return decorators
    
    def _extract_class_docstring(self, class_node: Node) -> Optional[str]:
        """Extract docstring from class body."""
        body_node = self.find_child_by_type(class_node, 'block')
        if not body_node or not body_node.children:
            return None
        
        first_stmt = body_node.children[0]
        if first_stmt.type == 'expression_statement':
            expr = self.find_child_by_type(first_stmt, 'string')
            if expr:
                docstring = self.get_node_text(expr)
                docstring = docstring.strip('"""').strip("'''").strip('"').strip("'")
                return docstring.strip()
        
        return None
    
    def extract_imports(self) -> List[ImportInfo]:
        """
        Extract all import statements from Python code.
        
        Returns:
            List of ImportInfo objects
        """
        imports = []
        self._extract_imports_recursive(self.root, imports)
        return imports
    
    def _extract_imports_recursive(self, node: Node, imports: List[ImportInfo]):
        """Recursively extract imports from node tree."""
        if node.type == 'import_statement':
            import_info = self._parse_import(node)
            if import_info:
                imports.extend(import_info)
        elif node.type == 'import_from_statement':
            import_info = self._parse_from_import(node)
            if import_info:
                imports.append(import_info)
        
        for child in node.children:
            self._extract_imports_recursive(child, imports)
    
    def _parse_import(self, node: Node) -> List[ImportInfo]:
        """Parse 'import x' statement."""
        imports = []
        for child in node.children:
            if child.type == 'dotted_name':
                module = self.get_node_text(child)
                imports.append(ImportInfo(
                    module=module,
                    names=[],
                    is_from_import=False,
                    start_line=node.start_point[0] + 1
                ))
            elif child.type == 'aliased_import':
                # import x as y
                name_node = self.find_child_by_type(child, 'dotted_name')
                alias_node = self.find_child_by_type(child, 'identifier')
                if name_node:
                    module = self.get_node_text(name_node)
                    alias = self.get_node_text(alias_node) if alias_node else None
                    imports.append(ImportInfo(
                        module=module,
                        names=[],
                        alias=alias,
                        is_from_import=False,
                        start_line=node.start_point[0] + 1
                    ))
        return imports
    
    def _parse_from_import(self, node: Node) -> Optional[ImportInfo]:
        """Parse 'from x import y' statement."""
        # Get module name
        module_node = self.find_child_by_type(node, 'dotted_name')
        if not module_node:
            return None
        module = self.get_node_text(module_node)
        
        # Get imported names
        names = []
        for child in node.children:
            if child.type == 'dotted_name' and child != module_node:
                names.append(self.get_node_text(child))
            elif child.type == 'identifier':
                names.append(self.get_node_text(child))
            elif child.type == 'aliased_import':
                name_node = self.find_child_by_type(child, 'identifier')
                if name_node:
                    names.append(self.get_node_text(name_node))
        
        return ImportInfo(
            module=module,
            names=names,
            is_from_import=True,
            start_line=node.start_point[0] + 1
        )


__all__ = ['PythonExtractor']
