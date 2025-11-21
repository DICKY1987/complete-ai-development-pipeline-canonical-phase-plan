#!/usr/bin/env python3
"""
Spec Resolver - Cross-reference resolver and validator for Game Board Protocol specs

This module provides functionality to:
- Parse specification documents (UPS, PPS, DR)
- Load and query metadata indices
- Resolve cross-references between specs
- Validate reference integrity
- Find all references to a section
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass


@dataclass
class Section:
    """Represents a section in a specification document"""
    section_id: str
    title: str
    document_id: str
    file_path: str
    line_start: Optional[int] = None
    level: Optional[int] = None
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None


@dataclass
class Reference:
    """Represents a cross-reference from one section to another"""
    from_section: str
    to_section: str
    reference_type: str  # 'specification', 'component', 'section'
    context: Optional[str] = None


class SpecResolver:
    """Resolves and validates cross-references between specification documents"""
    
    def __init__(self, base_path: Path = None):
        """
        Initialize the spec resolver
        
        Args:
            base_path: Base directory containing specs/ folder (defaults to current dir)
        """
        self.base_path = base_path or Path.cwd()
        self.specs_path = self.base_path / "specs"
        self.metadata_path = self.specs_path / "metadata"
        
        # Storage for loaded data
        self.sections: Dict[str, Section] = {}
        self.references: List[Reference] = []
        self.indices: Dict[str, dict] = {}
        
    def load_indices(self) -> bool:
        """
        Load all metadata indices
        
        Returns:
            True if successful, False otherwise
        """
        index_files = {
            'UPS': 'ups_index.json',
            'PPS': 'pps_index.json',
            'DR': 'dr_index.json'
        }
        
        for doc_id, filename in index_files.items():
            index_path = self.metadata_path / filename
            if not index_path.exists():
                print(f"Error: Index file not found: {index_path}", file=sys.stderr)
                return False
                
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    self.indices[doc_id] = index_data
                    self._load_sections_from_index(doc_id, index_data)
            except json.JSONDecodeError as e:
                print(f"Error parsing {filename}: {e}", file=sys.stderr)
                return False
                
        return True
    
    def _load_sections_from_index(self, doc_id: str, index_data: dict):
        """Load sections from an index into the sections dictionary"""
        document_id = index_data.get('document_id', doc_id)
        file_path = index_data.get('file_path', '')
        
        for section in index_data.get('sections', []):
            section_id = section.get('section_id')
            if section_id:
                self.sections[section_id] = Section(
                    section_id=section_id,
                    title=section.get('title', ''),
                    document_id=document_id,
                    file_path=file_path,
                    line_start=section.get('line_start'),
                    level=section.get('level', 2),
                    summary=section.get('summary'),
                    keywords=section.get('keywords', [])
                )
                
                # Also load subsections
                for subsection in section.get('subsections', []):
                    sub_id = subsection.get('id')
                    if sub_id:
                        self.sections[sub_id] = Section(
                            section_id=sub_id,
                            title=subsection.get('title', ''),
                            document_id=document_id,
                            file_path=file_path,
                            level=3,
                            keywords=subsection.get('keywords', [])
                        )
    
    def parse_all(self) -> bool:
        """
        Parse all specification documents and load metadata
        
        Returns:
            True if all specs parsed successfully
        """
        if not self.load_indices():
            return False
            
        print(f"[OK] Loaded {len(self.sections)} sections from {len(self.indices)} indices")
        return True
    
    def lookup(self, section_id: str) -> Optional[Section]:
        """
        Look up a section by its ID
        
        Args:
            section_id: Section ID (e.g., 'UPS-001', 'DR-DO-001')
            
        Returns:
            Section object if found, None otherwise
        """
        return self.sections.get(section_id)
    
    def find_references_to(self, section_id: str) -> List[str]:
        """
        Find all sections that reference the given section
        
        Args:
            section_id: Section ID to search for
            
        Returns:
            List of section IDs that reference the target section
        """
        references = []
        
        # Search through all indices for cross-references
        for doc_id, index_data in self.indices.items():
            for section in index_data.get('sections', []):
                # Check if section has references
                refs = section.get('references', [])
                for ref in refs:
                    ref_id = ref.get('id', '')
                    # Check if ref_id pattern matches section_id
                    if self._matches_pattern(ref_id, section_id):
                        references.append(section.get('section_id'))
                        
        return references
    
    def _matches_pattern(self, pattern: str, section_id: str) -> bool:
        """Check if a section ID matches a reference pattern"""
        # Handle wildcard patterns like 'UPS-*', 'DR-DO-*'
        if '*' in pattern:
            pattern_prefix = pattern.replace('*', '')
            return section_id.startswith(pattern_prefix)
        return pattern == section_id
    
    def validate_spec(self, spec_path: str) -> Tuple[bool, List[str]]:
        """
        Validate cross-references in a specification document
        
        Args:
            spec_path: Path to specification markdown file
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        spec_file = Path(spec_path)
        if not spec_file.exists():
            return False, [f"Specification file not found: {spec_path}"]
        
        errors = []
        
        try:
            with open(spec_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all section ID references in the content
            # Pattern: matches UPS-001, PPS-002-1, DR-DO-003, etc.
            ref_pattern = r'\b(UPS|PPS|DR(?:-(?:DO|DONT|GOLD))?)-\d{3}(?:-\d+)?\b'
            found_refs = re.findall(ref_pattern, content)
            
            # Build set of unique references
            unique_refs = set()
            for match in re.finditer(ref_pattern, content):
                unique_refs.add(match.group(0))
            
            # Validate each reference
            for ref_id in unique_refs:
                if ref_id not in self.sections:
                    # Check if it's a valid pattern reference (like UPS-*)
                    if not ref_id.endswith('*'):
                        errors.append(f"Broken reference: {ref_id} not found in any index")
            
        except Exception as e:
            errors.append(f"Error reading spec file: {e}")
            return False, errors
        
        return len(errors) == 0, errors
    
    def get_all_section_ids(self) -> List[str]:
        """Get list of all known section IDs"""
        return sorted(self.sections.keys())
    
    def search_by_keyword(self, keyword: str) -> List[Section]:
        """
        Search for sections by keyword
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching sections
        """
        results = []
        keyword_lower = keyword.lower()
        
        for section in self.sections.values():
            if section.keywords:
                if any(keyword_lower in kw.lower() for kw in section.keywords):
                    results.append(section)
            elif section.title and keyword_lower in section.title.lower():
                results.append(section)
                
        return results
    
    def print_section(self, section: Section):
        """Pretty print a section"""
        print(f"Section ID: {section.section_id}")
        print(f"  Title: {section.title}")
        print(f"  Document: {section.document_id}")
        print(f"  File: {section.file_path}")
        if section.line_start:
            print(f"  Line: {section.line_start}")
        if section.summary:
            print(f"  Summary: {section.summary}")
        if section.keywords:
            print(f"  Keywords: {', '.join(section.keywords)}")


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Game Board Protocol Spec Resolver')
    parser.add_argument('--parse-all', action='store_true',
                        help='Parse all spec documents and load indices')
    parser.add_argument('--validate', action='store_true',
                        help='Validate cross-references in a spec')
    parser.add_argument('--spec', type=str,
                        help='Specification file to validate')
    parser.add_argument('--lookup', type=str,
                        help='Look up a section by ID')
    parser.add_argument('--find-refs', type=str,
                        help='Find all references to a section')
    parser.add_argument('--search', type=str,
                        help='Search sections by keyword')
    parser.add_argument('--list-all', action='store_true',
                        help='List all section IDs')
    
    args = parser.parse_args()
    
    resolver = SpecResolver()
    
    # Load indices first
    if not resolver.load_indices():
        print("Error: Failed to load indices", file=sys.stderr)
        sys.exit(1)
    
    if args.parse_all:
        if resolver.parse_all():
            print(f"[OK] Successfully parsed all specs")
            print(f"  Total sections: {len(resolver.sections)}")
            print(f"  Total indices: {len(resolver.indices)}")
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.lookup:
        section = resolver.lookup(args.lookup)
        if section:
            resolver.print_section(section)
            sys.exit(0)
        else:
            print(f"Section not found: {args.lookup}", file=sys.stderr)
            sys.exit(1)
    
    elif args.find_refs:
        refs = resolver.find_references_to(args.find_refs)
        if refs:
            print(f"Sections referencing {args.find_refs}:")
            for ref in refs:
                print(f"  - {ref}")
            sys.exit(0)
        else:
            print(f"No references found to {args.find_refs}")
            sys.exit(0)
    
    elif args.validate:
        if not args.spec:
            print("Error: --spec required with --validate", file=sys.stderr)
            sys.exit(1)
        
        is_valid, errors = resolver.validate_spec(args.spec)
        if is_valid:
            print(f"[OK] {args.spec}: 0 broken references")
            sys.exit(0)
        else:
            print(f"[FAIL] {args.spec}: {len(errors)} broken reference(s)")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
    
    elif args.search:
        results = resolver.search_by_keyword(args.search)
        print(f"Found {len(results)} section(s) matching '{args.search}':")
        for section in results:
            print(f"  {section.section_id}: {section.title}")
        sys.exit(0)
    
    elif args.list_all:
        all_ids = resolver.get_all_section_ids()
        print(f"Total section IDs: {len(all_ids)}")
        for section_id in all_ids:
            print(f"  {section_id}")
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
