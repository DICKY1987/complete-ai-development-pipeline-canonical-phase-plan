#!/usr/bin/env python3
"""
Glossary SSOT Policy Validator

Enforces the rule: "Every SSOT document must have a glossary term."

Usage:
    python scripts/glossary_ssot_policy.py              # Validate only
    python scripts/glossary_ssot_policy.py --autofix    # Auto-generate missing terms (future)
    python scripts/glossary_ssot_policy.py --verbose    # Show detailed output

Exit codes:
    0 - All validations passed
    1 - Validation errors found
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
import fnmatch

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class SSOTDoc:
    """Represents a discovered SSOT document."""
    path: str
    doc_id: str | None
    scope: List[str]
    
    @property
    def has_doc_id(self) -> bool:
        return self.doc_id is not None and self.doc_id.strip() != ""


class GlossarySSOTPolicy:
    """Validates SSOT document ↔ glossary term consistency."""
    
    def __init__(self, config_path: Path = None, verbose: bool = False):
        if config_path is None:
            config_path = ROOT / "glossary/config/glossary_ssot_policy.yaml"
        
        self.config = self._load_config(config_path)
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def _load_config(self, path: Path) -> dict:
        """Load policy configuration."""
        if not path.exists():
            raise FileNotFoundError(f"Policy config not found: {path}")
        return yaml.safe_load(path.read_text())["ssot_policy"]
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if path matches exclusion patterns."""
        rel_path = str(path.relative_to(ROOT))
        for pattern in self.config.get("exclude_patterns", []):
            if fnmatch.fnmatch(rel_path, pattern):
                return True
        return False
    
    def _extract_frontmatter(self, text: str) -> dict | None:
        """Extract YAML front-matter from markdown document."""
        text = text.lstrip()
        if not text.startswith("---"):
            return None
        
        fm_end = text.find("\n---", 3)
        if fm_end == -1:
            return None
        
        try:
            front = text[3:fm_end]
            return yaml.safe_load(front) or {}
        except yaml.YAMLError:
            return None
    
    def find_ssot_docs(self) -> List[SSOTDoc]:
        """Discover all documents marked as SSOT."""
        ssot_docs = []
        ssot_field = self.config["ssot_frontmatter_field"]
        scope_field = self.config["ssot_scope_field"]
        doc_id_field = self.config["doc_id_field"]
        
        for path in ROOT.rglob("*.md"):
            if self._should_exclude(path):
                continue
            
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
                fm = self._extract_frontmatter(text)
                
                if fm and fm.get(ssot_field, False):
                    doc = SSOTDoc(
                        path=str(path.relative_to(ROOT)).replace("\\", "/"),
                        doc_id=fm.get(doc_id_field),
                        scope=fm.get(scope_field, [])
                    )
                    ssot_docs.append(doc)
                    
                    if self.verbose:
                        print(f"[SSOT] Found: {doc.path} (doc_id={doc.doc_id})")
            
            except Exception as e:
                if self.verbose:
                    print(f"[WARN] Error reading {path}: {e}")
        
        return ssot_docs
    
    def load_glossary_terms(self) -> dict:
        """Load glossary metadata."""
        meta_path = ROOT / self.config["glossary_metadata_file"]
        if not meta_path.exists():
            return {}
        
        data = yaml.safe_load(meta_path.read_text()) or {}
        # Extract terms dict from metadata structure
        return data.get("terms", {})
    
    def build_file_to_terms_index(self, terms: dict) -> Dict[str, List[str]]:
        """Build reverse index: file_path -> [term_ids]."""
        file_to_terms = {}
        valid_categories = set(self.config["term_categories"])
        
        for term_id, term in terms.items():
            category = term.get("category", "")
            
            # Only index terms in SSOT-related categories
            if category not in valid_categories:
                continue
            
            impl = term.get("implementation", {})
            files = impl.get("files", [])
            
            for f in files:
                # Normalize path separators
                f = f.replace("\\", "/")
                file_to_terms.setdefault(f, []).append(term_id)
        
        return file_to_terms
    
    def validate_ssot_docs_have_terms(
        self, 
        ssot_docs: List[SSOTDoc], 
        file_to_terms: Dict[str, List[str]]
    ):
        """Validate each SSOT doc has at least one glossary term."""
        for doc in ssot_docs:
            if doc.path not in file_to_terms:
                msg_template = self.config["messages"]["ssot_doc_no_term"]
                msg = msg_template.format(
                    path=doc.path,
                    doc_id=doc.doc_id or "MISSING"
                )
                self.errors.append(msg)
    
    def validate_ssot_docs_have_doc_ids(self, ssot_docs: List[SSOTDoc]):
        """Validate each SSOT doc has a doc_id."""
        if not self.config["ci"]["fail_on_ssot_doc_missing_doc_id"]:
            return
        
        for doc in ssot_docs:
            if not doc.has_doc_id:
                msg_template = self.config["messages"]["ssot_no_doc_id"]
                msg = msg_template.format(path=doc.path)
                self.errors.append(msg)
    
    def validate_terms_point_to_existing_files(self, terms: dict):
        """Validate each SSOT term references existing files."""
        valid_categories = set(self.config["term_categories"])
        
        for term_id, term in terms.items():
            category = term.get("category", "")
            
            if category not in valid_categories:
                continue
            
            impl = term.get("implementation", {})
            files = impl.get("files", [])
            
            for f in files:
                # Normalize path separators
                f_normalized = f.replace("\\", "/")
                file_path = ROOT / f_normalized
                
                if not file_path.exists():
                    msg_template = self.config["messages"]["term_missing_file"]
                    msg = msg_template.format(
                        term_id=term_id,
                        file_path=f
                    )
                    self.errors.append(msg)
    
    def validate(self) -> bool:
        """Run all validations. Returns True if all pass."""
        if self.verbose:
            print("\n=== Glossary SSOT Policy Validation ===\n")
        
        # 1. Discover SSOT documents
        ssot_docs = self.find_ssot_docs()
        if self.verbose:
            print(f"\nFound {len(ssot_docs)} SSOT documents\n")
        
        # 2. Load glossary
        terms = self.load_glossary_terms()
        if self.verbose:
            print(f"Loaded {len(terms)} glossary terms\n")
        
        # 3. Build index
        file_to_terms = self.build_file_to_terms_index(terms)
        
        # 4. Run validations
        self.validate_ssot_docs_have_doc_ids(ssot_docs)
        self.validate_ssot_docs_have_terms(ssot_docs, file_to_terms)
        self.validate_terms_point_to_existing_files(terms)
        
        # 5. Report results
        return self._report_results()
    
    def _report_results(self) -> bool:
        """Print validation results. Returns True if no errors."""
        if self.warnings:
            print("\n⚠️  WARNINGS:\n")
            for warning in self.warnings:
                print(warning)
                print()
        
        if self.errors:
            print("\n❌ ERRORS:\n")
            for error in self.errors:
                print(error)
                print()
            
            if self.config["ci"]["fail_on_missing_term_for_ssot_doc"]:
                print(f"Found {len(self.errors)} policy violation(s)")
                return False
        
        if not self.errors and not self.warnings:
            print("✅ All SSOT policy validations passed")
        
        return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate glossary SSOT policy compliance"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--autofix",
        action="store_true",
        help="Auto-generate missing glossary terms (not yet implemented)"
    )
    
    args = parser.parse_args()
    
    if args.autofix:
        print("❌ --autofix not yet implemented")
        sys.exit(1)
    
    validator = GlossarySSOTPolicy(verbose=args.verbose)
    success = validator.validate()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
