#!/usr/bin/env python3
"""
WORKSTREAM_V1.1 Prompt Renderer - PH-3A

Generates AI-optimized prompts from phase specifications in WORKSTREAM_V1.1 format.
Embeds context from specification sections and formats for optimal AI comprehension.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import spec renderer
sys.path.insert(0, str(Path(__file__).parent))
from spec_renderer import SpecRenderer


class PromptRenderer:
    """Generate WORKSTREAM_V1.1 format prompts from phase specifications."""
    
    def __init__(self):
        self.spec_renderer = SpecRenderer()
        self.template_path = Path("templates/workstream_v1.1.txt")
    
    def render_prompt(
        self,
        phase_spec: Dict[str, Any],
        embed_specs: bool = False
    ) -> str:
        """
        Render a WORKSTREAM_V1.1 prompt from phase specification.
        
        Args:
            phase_spec: Phase specification dictionary
            embed_specs: Whether to embed referenced spec sections
        
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # Header
        prompt_parts.append(self._render_header(phase_spec))
        
        # Objective
        prompt_parts.append(self._render_objective(phase_spec))
        
        # Context (if embedding specs)
        if embed_specs:
            prompt_parts.append(self._render_embedded_context(phase_spec))
        
        # Pre-flight checks
        prompt_parts.append(self._render_pre_flight_checks(phase_spec))
        
        # File scope
        prompt_parts.append(self._render_file_scope(phase_spec))
        
        # Deliverables
        prompt_parts.append(self._render_deliverables(phase_spec))
        
        # Acceptance tests (completion criteria)
        prompt_parts.append(self._render_acceptance_tests(phase_spec))
        
        # Dependencies
        prompt_parts.append(self._render_dependencies(phase_spec))
        
        # Footer
        prompt_parts.append(self._render_footer(phase_spec))
        
        return "\n\n".join(prompt_parts)
    
    def _render_header(self, spec: Dict[str, Any]) -> str:
        """Render prompt header."""
        phase_id = spec.get("phase_id", "UNKNOWN")
        phase_name = spec.get("phase_name", "Unnamed Phase")
        
        header = f"""{'=' * 80}
WORKSTREAM_V1.1: AI-ASSISTED DEVELOPMENT PROTOCOL
{'=' * 80}

PHASE_ID: {phase_id}
PHASE_NAME: {phase_name}

This is a structured development workstream following the Game Board Protocol.
You are an AI development assistant tasked with executing this phase."""
        
        return header
    
    def _render_objective(self, spec: Dict[str, Any]) -> str:
        """Render objective section."""
        objective = spec.get("objective", "No objective specified")
        
        return f"""OBJECTIVE:
{'-' * 80}
{objective}

Your task is to implement this objective while following all specifications,
passing all acceptance tests, and delivering all required artifacts."""
    
    def _render_embedded_context(self, spec: Dict[str, Any]) -> str:
        """Render embedded specification context."""
        context_parts = [
            "EMBEDDED_SPECIFICATION_CONTEXT:",
            "-" * 80,
            "The following specification sections provide detailed requirements:",
            ""
        ]
        
        # Extract references from objective and notes
        objective = spec.get("objective", "")
        notes = spec.get("notes", "")
        combined_text = f"{objective} {notes}"
        
        # Simple pattern matching for spec IDs
        import re
        spec_ids = set()
        patterns = [
            r'\b(UPS-\d{3}(?:-\d+)?)\b',
            r'\b(PPS-\d{3}(?:-\d+)?)\b',
            r'\b(DR-(?:DO|DONT|GOLD)-\d{3}(?:-\d+)?)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, combined_text)
            spec_ids.update(matches)
        
        if spec_ids:
            for spec_id in sorted(spec_ids):
                section_content = self.spec_renderer.render_section(
                    spec_id,
                    format="prompt",
                    include_deps=False
                )
                context_parts.append(section_content)
                context_parts.append("")
        else:
            context_parts.append("(No specific specification sections referenced)")
        
        return "\n".join(context_parts)
    
    def _render_pre_flight_checks(self, spec: Dict[str, Any]) -> str:
        """Render pre-flight checks section."""
        checks = spec.get("pre_flight_checks", [])
        
        lines = [
            "PRE_FLIGHT_CHECKS:",
            "-" * 80,
            "Execute these checks BEFORE beginning implementation:",
            ""
        ]
        
        if checks:
            for i, check in enumerate(checks, 1):
                check_id = check.get("check_id", f"CHECK-{i:03d}")
                description = check.get("description", "No description")
                command = check.get("command", "")
                expected = check.get("expected", "")
                
                lines.append(f"{i}. {check_id}: {description}")
                if command:
                    lines.append(f"   Command: {command}")
                if expected:
                    lines.append(f"   Expected: {expected}")
                lines.append("")
        else:
            lines.append("(No pre-flight checks specified)")
        
        return "\n".join(lines)
    
    def _render_file_scope(self, spec: Dict[str, Any]) -> str:
        """Render file scope section."""
        file_scope = spec.get("file_scope", [])
        
        lines = [
            "FILE_SCOPE:",
            "-" * 80,
            "You may ONLY create or modify the following files:",
            ""
        ]
        
        if file_scope:
            for filepath in file_scope:
                lines.append(f"  - {filepath}")
        else:
            lines.append("(No files specified)")
        
        lines.append("")
        lines.append("DO NOT modify any files outside this scope.")
        
        return "\n".join(lines)
    
    def _render_deliverables(self, spec: Dict[str, Any]) -> str:
        """Render deliverables section."""
        deliverables = spec.get("deliverables", [])
        
        lines = [
            "DELIVERABLES:",
            "-" * 80,
            "You must produce the following artifacts:",
            ""
        ]
        
        if deliverables:
            for i, deliverable in enumerate(deliverables, 1):
                lines.append(f"{i}. {deliverable}")
        else:
            lines.append("(No deliverables specified)")
        
        return "\n".join(lines)
    
    def _render_acceptance_tests(self, spec: Dict[str, Any]) -> str:
        """Render acceptance tests as completion criteria."""
        tests = spec.get("acceptance_tests", [])
        
        lines = [
            "ACCEPTANCE_TESTS (Completion Criteria):",
            "-" * 80,
            "Your implementation MUST pass ALL of these tests:",
            ""
        ]
        
        if tests:
            for i, test in enumerate(tests, 1):
                test_id = test.get("test_id", f"AT-{i:03d}")
                description = test.get("description", "No description")
                command = test.get("command", "")
                expected = test.get("expected", "")
                
                lines.append(f"ACCEPTANCE_TEST {i}: {test_id}")
                lines.append(f"  Description: {description}")
                if command:
                    lines.append(f"  Command: {command}")
                if expected:
                    lines.append(f"  Expected: {expected}")
                lines.append("")
        else:
            lines.append("(No acceptance tests specified)")
        
        return "\n".join(lines)
    
    def _render_dependencies(self, spec: Dict[str, Any]) -> str:
        """Render dependencies section."""
        dependencies = spec.get("dependencies", [])
        
        lines = [
            "DEPENDENCIES:",
            "-" * 80
        ]
        
        if dependencies:
            lines.append("The following phases MUST be complete before executing this phase:")
            lines.append("")
            for dep in dependencies:
                lines.append(f"  - {dep}")
        else:
            lines.append("This phase has no dependencies.")
        
        return "\n".join(lines)
    
    def _render_footer(self, spec: Dict[str, Any]) -> str:
        """Render prompt footer."""
        effort_hours = spec.get("estimated_effort_hours", "Unknown")
        notes = spec.get("notes", "")
        
        footer = f"""{'=' * 80}
EXECUTION_METADATA:
{'-' * 80}
Estimated Effort: {effort_hours} hours
Risk Level: {spec.get('risk_level', 'medium')}"""
        
        if notes:
            footer += f"\n\nNOTES:\n{notes}"
        
        footer += f"""

{'=' * 80}
BEGIN IMPLEMENTATION
{'=' * 80}

Follow the WORKSTREAM_V1.1 protocol:
1. Run ALL pre-flight checks
2. Create/modify ONLY files in scope
3. Deliver ALL specified artifacts
4. Pass ALL acceptance tests
5. Document your work

Good luck! Let's build something great."""
        
        return footer
    
    def render_from_file(
        self,
        phase_spec_file: str,
        embed_specs: bool = False
    ) -> str:
        """
        Render prompt from phase specification file.
        
        Args:
            phase_spec_file: Path to phase spec JSON file
            embed_specs: Whether to embed referenced spec sections
        
        Returns:
            Formatted prompt string
        """
        try:
            with open(phase_spec_file, 'r', encoding='utf-8') as f:
                spec = json.load(f)
            
            return self.render_prompt(spec, embed_specs)
        
        except FileNotFoundError:
            return f"ERROR: Phase spec file not found: {phase_spec_file}"
        except json.JSONDecodeError as e:
            return f"ERROR: Invalid JSON in phase spec: {e.msg}"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def save_prompt(self, prompt: str, output_file: str) -> None:
        """Save rendered prompt to file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        print(f"Prompt saved to: {output_path}")


def main():
    """CLI entry point for prompt rendering."""
    parser = argparse.ArgumentParser(
        description="Generate WORKSTREAM_V1.1 prompts from phase specifications"
    )
    parser.add_argument(
        "--phase",
        type=str,
        required=True,
        help="Path to phase specification JSON file"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (prints to stdout if not specified)"
    )
    parser.add_argument(
        "--embed-specs",
        action="store_true",
        help="Embed referenced specification sections as context"
    )
    
    args = parser.parse_args()
    
    try:
        renderer = PromptRenderer()
        prompt = renderer.render_from_file(args.phase, args.embed_specs)
        
        if args.output:
            renderer.save_prompt(prompt, args.output)
        else:
            print(prompt)
        
        return 0
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
