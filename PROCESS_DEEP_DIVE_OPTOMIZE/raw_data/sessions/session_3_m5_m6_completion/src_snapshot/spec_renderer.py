#!/usr/bin/env python3
"""
Spec Renderer - PH-1F

Renders specification sections into multiple formats (markdown, prompt, HTML)
with proper formatting, dependency resolution, and context bundling for AI prompts.
"""

import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Set


class SpecRenderer:
    """Render specification sections into various formats."""
    
    def __init__(self, specs_dir: str = "specs", metadata_dir: str = "specs/metadata"):
        self.specs_dir = Path(specs_dir)
        self.metadata_dir = Path(metadata_dir)
        self.indices = self._load_all_indices()
        self.specs_content = self._load_all_specs()
    
    def _load_all_indices(self) -> Dict[str, Any]:
        """Load all metadata indices."""
        indices = {}
        index_files = {
            "UPS": "ups_index.json",
            "PPS": "pps_index.json",
            "DR": "dr_index.json"
        }
        
        for prefix, filename in index_files.items():
            path = self.metadata_dir / filename
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    indices[prefix] = json.load(f)
        
        return indices
    
    def _load_all_specs(self) -> Dict[str, str]:
        """Load all specification document contents."""
        specs = {}
        spec_files = {
            "UPS": "UNIVERSAL_PHASE_SPEC_V1.md",
            "PPS": "PRO_PHASE_SPEC_V1.md",
            "DR": "DEV_RULES_V1.md"
        }
        
        for prefix, filename in spec_files.items():
            path = self.specs_dir / filename
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    specs[prefix] = f.read()
        
        return specs
    
    def _get_spec_type(self, section_id: str) -> Optional[str]:
        """Determine spec type from section ID."""
        if section_id.startswith("UPS-"):
            return "UPS"
        elif section_id.startswith("PPS-"):
            return "PPS"
        elif section_id.startswith("DR-"):
            return "DR"
        return None
    
    def _extract_section_content(self, spec_type: str, section_id: str) -> Optional[str]:
        """Extract section content from specification document."""
        if spec_type not in self.specs_content:
            return None
        
        content = self.specs_content[spec_type]
        
        # Find section by anchor
        pattern = rf"(##[^#].*?\{{#{re.escape(section_id)}\}})(.*?)(?=##[^#]|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            heading = match.group(1).strip()
            body = match.group(2).strip()
            return f"{heading}\n\n{body}"
        
        return None
    
    def _find_section_metadata(self, section_id: str) -> Optional[Dict[str, Any]]:
        """Find section metadata from indices."""
        spec_type = self._get_spec_type(section_id)
        if not spec_type or spec_type not in self.indices:
            return None
        
        index = self.indices[spec_type]
        for section in index.get("sections", []):
            if section.get("section_id") == section_id:
                return section
            # Check subsections
            for subsection in section.get("subsections", []):
                if subsection.get("section_id") == section_id:
                    return subsection
        
        return None
    
    def _extract_references(self, content: str) -> Set[str]:
        """Extract all section ID references from content."""
        references = set()
        patterns = [
            r'\b(UPS-\d{3}(?:-\d+)?)\b',
            r'\b(PPS-\d{3}(?:-\d+)?)\b',
            r'\b(DR-(?:DO|DONT|GOLD)-\d{3}(?:-\d+)?)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            references.update(matches)
        
        return references
    
    def render_section(
        self,
        section_id: str,
        format: str = "markdown",
        include_deps: bool = False
    ) -> str:
        """
        Render a single section by ID.
        
        Args:
            section_id: Section ID (e.g., UPS-001, DR-DO-001)
            format: Output format (markdown, prompt, html)
            include_deps: Include referenced sections
        
        Returns:
            Rendered content string
        """
        spec_type = self._get_spec_type(section_id)
        if not spec_type:
            return f"ERROR: Invalid section ID: {section_id}"
        
        content = self._extract_section_content(spec_type, section_id)
        if not content:
            return f"ERROR: Section not found: {section_id}"
        
        metadata = self._find_section_metadata(section_id)
        
        if format == "markdown":
            output = self._render_markdown(section_id, content, metadata)
        elif format == "prompt":
            output = self._render_prompt(section_id, content, metadata)
        elif format == "html":
            output = self._render_html(section_id, content, metadata)
        else:
            return f"ERROR: Unknown format: {format}"
        
        if include_deps:
            refs = self._extract_references(content)
            if refs:
                output += "\n\n" + "=" * 80 + "\n"
                output += "## Referenced Sections\n\n"
                for ref in sorted(refs):
                    if ref != section_id:
                        ref_content = self.render_section(ref, format, include_deps=False)
                        output += f"\n{ref_content}\n"
        
        return output
    
    def _render_markdown(
        self,
        section_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]]
    ) -> str:
        """Render section in markdown format."""
        output = f"<!-- Section: {section_id} -->\n"
        
        if metadata:
            output += f"<!-- Keywords: {', '.join(metadata.get('keywords', []))} -->\n"
        
        output += f"\n{content}\n"
        return output
    
    def _render_prompt(
        self,
        section_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]]
    ) -> str:
        """Render section in ASCII-only prompt format."""
        # Remove markdown formatting for cleaner prompt text
        prompt_content = content
        
        # Remove anchor syntax
        prompt_content = re.sub(r'\s*\{#[^}]+\}', '', prompt_content)
        
        # Convert markdown headers to plain text
        prompt_content = re.sub(r'^###\s+', '   ', prompt_content, flags=re.MULTILINE)
        prompt_content = re.sub(r'^##\s+', '  ', prompt_content, flags=re.MULTILINE)
        prompt_content = re.sub(r'^#\s+', '', prompt_content, flags=re.MULTILINE)
        
        # Remove bold/italic
        prompt_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', prompt_content)
        prompt_content = re.sub(r'\*([^*]+)\*', r'\1', prompt_content)
        
        # Convert code blocks to indented text
        prompt_content = re.sub(r'```[a-z]*\n', '\n', prompt_content)
        prompt_content = re.sub(r'```', '', prompt_content)
        
        output = f"[Section: {section_id}]\n"
        output += "=" * 60 + "\n"
        if metadata:
            keywords = metadata.get('keywords', [])
            if keywords:
                output += f"Keywords: {', '.join(keywords)}\n"
                output += "-" * 60 + "\n"
        
        output += f"\n{prompt_content}\n"
        return output
    
    def _render_html(
        self,
        section_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]]
    ) -> str:
        """Render section in HTML format."""
        output = f'<div class="spec-section" id="{section_id}">\n'
        
        if metadata:
            keywords = metadata.get('keywords', [])
            if keywords:
                tags = " ".join([f'<span class="keyword">{kw}</span>' for kw in keywords])
                output += f'  <div class="keywords">{tags}</div>\n'
        
        # Basic markdown to HTML conversion
        html_content = content
        html_content = re.sub(r'^### (.+)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^# (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html_content)
        html_content = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html_content)
        html_content = re.sub(r'`([^`]+)`', r'<code>\1</code>', html_content)
        
        output += f'  <div class="content">\n{html_content}\n  </div>\n'
        output += '</div>\n'
        
        return output
    
    def bundle_sections(
        self,
        section_ids: List[str],
        format: str = "markdown",
        include_deps: bool = False
    ) -> str:
        """Bundle multiple sections into a single context."""
        output = f"# Game Board Protocol - Context Bundle\n\n"
        output += f"**Sections:** {', '.join(section_ids)}\n"
        output += f"**Format:** {format}\n\n"
        output += "=" * 80 + "\n\n"
        
        for section_id in section_ids:
            section_content = self.render_section(section_id, format, include_deps)
            output += section_content + "\n\n"
            output += "-" * 80 + "\n\n"
        
        return output
    
    def save_output(self, content: str, output_path: str) -> None:
        """Save rendered content to file."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Output saved to: {output}")


def main():
    """CLI entry point for spec rendering."""
    parser = argparse.ArgumentParser(
        description="Render Game Board Protocol specification sections"
    )
    parser.add_argument(
        "--render",
        type=str,
        help="Section ID to render (e.g., UPS-001, DR-DO-001)"
    )
    parser.add_argument(
        "--bundle",
        type=str,
        help="Comma-separated list of section IDs to bundle"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "prompt", "html"],
        default="markdown",
        help="Output format"
    )
    parser.add_argument(
        "--include-deps",
        action="store_true",
        help="Include referenced sections"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (prints to stdout if not specified)"
    )
    
    args = parser.parse_args()
    
    if not args.render and not args.bundle:
        parser.error("Either --render or --bundle must be specified")
    
    try:
        renderer = SpecRenderer()
        
        if args.render:
            content = renderer.render_section(
                args.render,
                format=args.format,
                include_deps=args.include_deps
            )
        elif args.bundle:
            section_ids = [sid.strip() for sid in args.bundle.split(',')]
            content = renderer.bundle_sections(
                section_ids,
                format=args.format,
                include_deps=args.include_deps
            )
        
        if args.output:
            renderer.save_output(content, args.output)
        else:
            print(content)
        
        return 0
    
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
