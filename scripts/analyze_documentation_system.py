#!/usr/bin/env python3
"""
Documentation System State Analysis CLI

Analyzes the current repository and documentation state relative to
the documentation quality, coverage, and automation requirements outlined in
DOC-DOCS-SYSTEM-STATE-ANALYSIS-CLI-001.

This tool produces a machine-readable report describing:
- SSOT coverage (22 categories)
- Link integrity (doc_id, pattern_id, module_id, phase_id)
- Automation state (generators, validators, CI jobs)
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import yaml


# SSOT Categories from the brief (Section 3.2)
SSOT_CATEGORIES = {
    "repo_foundations": [
        "Glossary & Vocabulary",
        "Phase Model (0-7)",
        "Module & Folder Taxonomy",
        "ID & Registry Scheme",
    ],
    "execution_orchestration": [
        "Task Lifecycle / State Machine",
        "Orchestrator Execution Contract",
        "Deterministic Mode / Safety Profile",
        "Error Handling & Escalation Pipeline",
        "Automation Health & Coverage",
    ],
    "pattern_validation": [
        "Pattern Architecture & PAT-CHECK Rules",
        "Doc Types & Frontmatter Schemas",
        "README Structure & Doc Style",
    ],
    "git_workflow": [
        "Branching & Multi-Agent Strategy",
        "Safe Merge & Auto-Sync Strategy",
        "GitHub Project / Issues Integration",
    ],
    "tools_adapters": [
        "Tool Adapter Catalog",
        "OpenSpec → Pipeline Integration",
        "Claude Code Project Management (CCPM) Integration",
    ],
    "monitoring": [
        "Logging & Event Schema",
        "State Store & Registry Persistence",
        "GUI / Dashboard Contract",
    ],
    "modules": [
        "Module Contract & Responsibilities (per module)",
    ],
}


@dataclass
class SSOTCategoryStatus:
    """Status of a single SSOT category"""
    name: str
    expected: bool = True
    ssot_doc_found: bool = False
    ssot_doc_path: Optional[str] = None
    doc_id: Optional[str] = None
    status: str = "missing"  # ok | missing | candidate_only | duplicate
    notes: str = ""


@dataclass
class LinkIntegrity:
    """Link integrity analysis results"""
    doc_ids: Dict[str, any] = field(default_factory=dict)
    code_to_docs: Dict[str, List] = field(default_factory=dict)


@dataclass
class AutomationState:
    """Automation analysis results"""
    generators: Dict[str, any] = field(default_factory=dict)
    validators: Dict[str, any] = field(default_factory=dict)
    auto_sections: Dict[str, List] = field(default_factory=dict)
    scheduled_jobs: Dict[str, any] = field(default_factory=dict)


@dataclass
class OverallAssessment:
    """Overall assessment of documentation system"""
    summary: str = ""
    risk_level: str = "medium"  # low | medium | high
    key_findings: List[str] = field(default_factory=list)
    recommended_next_actions: List[Dict] = field(default_factory=list)


@dataclass
class DocumentationSystemReport:
    """Complete documentation system state report"""
    ssot_coverage: Dict[str, any] = field(default_factory=dict)
    link_integrity: LinkIntegrity = field(default_factory=LinkIntegrity)
    automation_state: AutomationState = field(default_factory=AutomationState)
    overall_assessment: OverallAssessment = field(default_factory=OverallAssessment)


class DocumentationAnalyzer:
    """Analyzes documentation system state"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.docs_with_ids: Dict[str, Dict] = {}
        self.all_doc_ids: Set[str] = set()
        self.all_pattern_ids: Set[str] = set()
        self.all_module_ids: Set[str] = set()
        self.all_phase_ids: Set[str] = set()
        self.registry_doc_ids: Set[str] = set()

    def analyze(self) -> DocumentationSystemReport:
        """Run complete analysis"""
        print("🔍 Scanning repository...")
        
        # Scan files
        self._scan_docs_for_ids()
        self._scan_registries()
        
        # Analyze components
        ssot_coverage = self._analyze_ssot_coverage()
        link_integrity = self._analyze_link_integrity()
        automation_state = self._analyze_automation_state()
        overall_assessment = self._assess_overall_state(
            ssot_coverage, link_integrity, automation_state
        )
        
        return DocumentationSystemReport(
            ssot_coverage=ssot_coverage,
            link_integrity=asdict(link_integrity),
            automation_state=asdict(automation_state),
            overall_assessment=asdict(overall_assessment),
        )

    def _scan_docs_for_ids(self):
        """Scan all markdown files for doc_id and related IDs"""
        md_files = list(self.repo_root.rglob("*.md"))
        print(f"  Found {len(md_files)} markdown files")
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                
                # Extract frontmatter
                frontmatter = self._extract_frontmatter(content)
                if frontmatter:
                    doc_id = frontmatter.get('doc_id')
                    if doc_id:
                        self.all_doc_ids.add(doc_id)
                        self.docs_with_ids[str(md_file.relative_to(self.repo_root))] = {
                            'doc_id': doc_id,
                            'frontmatter': frontmatter,
                            'path': str(md_file.relative_to(self.repo_root)),
                        }
                
                # Extract pattern_id, module_id, phase_id from content
                self._extract_ids_from_content(content)
                
            except Exception as e:
                print(f"  ⚠️  Error reading {md_file}: {e}")

    def _extract_frontmatter(self, content: str) -> Optional[Dict]:
        """Extract YAML frontmatter from markdown content"""
        # Match --- ... --- at start of file
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except yaml.YAMLError:
                return None
        return None

    def _extract_ids_from_content(self, content: str):
        """Extract various IDs from document content"""
        # Pattern IDs: PAT-*
        pattern_ids = re.findall(r'\bPAT-[\w-]+\b', content)
        self.all_pattern_ids.update(pattern_ids)
        
        # Module IDs: MOD-*
        module_ids = re.findall(r'\bMOD-[\w-]+\b', content)
        self.all_module_ids.update(module_ids)
        
        # Phase IDs: PH-*
        phase_ids = re.findall(r'\bPH-[\w-]+\b', content)
        self.all_phase_ids.update(phase_ids)

    def _scan_registries(self):
        """Scan registry files for doc_ids"""
        # PATTERN_INDEX.yaml
        pattern_index = self.repo_root / "patterns" / "registry" / "PATTERN_INDEX.yaml"
        if pattern_index.exists():
            try:
                data = yaml.safe_load(pattern_index.read_text())
                if data and 'doc_id' in data:
                    self.registry_doc_ids.add(data['doc_id'])
                if data and 'patterns' in data:
                    for pattern in data['patterns']:
                        if 'pattern_id' in pattern:
                            self.all_pattern_ids.add(pattern['pattern_id'])
            except Exception as e:
                print(f"  ⚠️  Error reading PATTERN_INDEX.yaml: {e}")
        
        # Look for other registry files
        for registry_file in self.repo_root.rglob("*registry*.yaml"):
            try:
                data = yaml.safe_load(registry_file.read_text())
                if isinstance(data, dict) and 'doc_id' in data:
                    self.registry_doc_ids.add(data['doc_id'])
            except:
                pass

    def _analyze_ssot_coverage(self) -> Dict:
        """Analyze SSOT coverage for all 22 categories"""
        categories = []
        total = 0
        
        # Flatten all categories
        all_ssot_categories = []
        for group_categories in SSOT_CATEGORIES.values():
            all_ssot_categories.extend(group_categories)
        
        total = len(all_ssot_categories)
        
        # Check each category
        for category_name in all_ssot_categories:
            status = self._check_ssot_category(category_name)
            categories.append(asdict(status))
        
        return {
            "total_categories": total,
            "categories": categories,
        }

    def _check_ssot_category(self, category_name: str) -> SSOTCategoryStatus:
        """Check if an SSOT doc exists for a category"""
        status = SSOTCategoryStatus(name=category_name)
        
        # Map category to expected files (heuristic)
        category_mapping = {
            "Glossary & Vocabulary": ["glossary/README.md", "glossary/glossary.md"],
            "Phase Model (0-7)": ["docs/Phase-Based AI Dev Pipeline (0–7) – Coherent Process.md"],
            "Module & Folder Taxonomy": ["README.md", "AGENTS.md"],
            "ID & Registry Scheme": ["specs/UTE_ID_SYSTEM_SPEC.md"],
            "Task Lifecycle / State Machine": ["docs/DOC_state_machines/STATE_MACHINES.md", "docs/DOC_execution_model/STATE_MACHINE.md"],
            "Orchestrator Execution Contract": ["docs/registry/REGISTRY_MAINTAINER_FOR_AI_CLI_SPEC.md"],
            "Error Handling & Escalation Pipeline": ["docs/DOC_reference/DOC_ERROR_CATALOG.md"],
            "Pattern Architecture & PAT-CHECK Rules": ["patterns/registry/PATTERN_INDEX.yaml"],
            "Branching & Multi-Agent Strategy": ["docs/DOC_operations/MULTI_AGENT_ORCHESTRATION_GUIDE.md"],
            "GitHub Project / Issues Integration": ["specs/README_GITHUB_PROJECT_INTEGRATION.md"],
        }
        
        expected_paths = category_mapping.get(category_name, [])
        
        for path in expected_paths:
            full_path = self.repo_root / path
            if full_path.exists():
                status.ssot_doc_found = True
                status.ssot_doc_path = path
                
                # Try to get doc_id
                if path.endswith('.md'):
                    try:
                        content = full_path.read_text()
                        frontmatter = self._extract_frontmatter(content)
                        if frontmatter and 'doc_id' in frontmatter:
                            status.doc_id = frontmatter['doc_id']
                            status.status = "ok"
                        else:
                            status.status = "candidate_only"
                            status.notes = "Found file but no doc_id in frontmatter"
                    except:
                        status.status = "candidate_only"
                elif path.endswith('.yaml'):
                    status.status = "ok"
                    status.notes = "Registry file found"
                
                break
        
        if not status.ssot_doc_found:
            status.status = "missing"
            status.notes = "No SSOT document found for this category"
        
        return status

    def _analyze_link_integrity(self) -> LinkIntegrity:
        """Analyze link integrity across the system"""
        integrity = LinkIntegrity()
        
        # Doc IDs analysis
        integrity.doc_ids = {
            "total_in_files": len(self.all_doc_ids),
            "total_in_registry": len(self.registry_doc_ids),
            "duplicates": self._find_duplicate_doc_ids(),
            "dangling_references": self._find_dangling_references(),
            "unregistered_ids": list(self.all_doc_ids - self.registry_doc_ids)[:10],  # Sample
        }
        
        # Code to docs analysis
        integrity.code_to_docs = {
            "implementations_without_docs": [],
            "docs_without_implementations": [],
            "invalid_doc_references_in_code": [],
        }
        
        return integrity

    def _find_duplicate_doc_ids(self) -> List[str]:
        """Find duplicate doc_ids"""
        doc_id_counts = {}
        for doc_info in self.docs_with_ids.values():
            doc_id = doc_info['doc_id']
            doc_id_counts[doc_id] = doc_id_counts.get(doc_id, 0) + 1
        
        return [doc_id for doc_id, count in doc_id_counts.items() if count > 1]

    def _find_dangling_references(self) -> List[Dict]:
        """Find references to non-existent doc_ids"""
        dangling = []
        
        # Check frontmatter references
        for doc_info in self.docs_with_ids.values():
            frontmatter = doc_info.get('frontmatter', {})
            related_ids = frontmatter.get('related_doc_ids', [])
            
            for ref_id in related_ids:
                if ref_id not in self.all_doc_ids:
                    dangling.append({
                        "from_doc": doc_info['doc_id'],
                        "missing_ref": ref_id,
                        "path": doc_info['path'],
                    })
        
        return dangling[:10]  # Sample

    def _analyze_automation_state(self) -> AutomationState:
        """Analyze automation state"""
        state = AutomationState()
        
        # Find generators
        scripts_dir = self.repo_root / "scripts"
        generators = []
        if scripts_dir.exists():
            for script in scripts_dir.glob("generate_*.py"):
                generators.append(str(script.name))
            for script in scripts_dir.glob("generate_*.ps1"):
                generators.append(str(script.name))
        
        state.generators = {
            "found": generators,
            "ssot_to_doc_mapping": [],
            "coverage_assessment": f"Found {len(generators)} generator scripts",
        }
        
        # Find validators
        validators = []
        wired_into_ci = []
        if scripts_dir.exists():
            for script in scripts_dir.glob("validate_*.py"):
                validators.append(str(script.name))
            for script in scripts_dir.glob("check_*.py"):
                validators.append(str(script.name))
        
        # Check CI workflows
        workflows_dir = self.repo_root / ".github" / "workflows"
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    for validator in validators:
                        if validator in content:
                            wired_into_ci.append(validator)
                except:
                    pass
        
        state.validators = {
            "found": validators,
            "wired_into_ci": list(set(wired_into_ci)),
            "not_wired": list(set(validators) - set(wired_into_ci)),
            "missing_but_expected": [],
        }
        
        # Find auto-updated sections
        docs_with_auto = []
        for md_file in self.repo_root.rglob("*.md"):
            try:
                content = md_file.read_text()
                if "<!-- AUTO:" in content or "<!-- END_AUTO:" in content:
                    docs_with_auto.append(str(md_file.relative_to(self.repo_root)))
            except:
                pass
        
        state.auto_sections = {
            "docs_with_auto_blocks": docs_with_auto[:10],  # Sample
            "stale_or_inconsistent": [],
        }
        
        # Find scheduled jobs
        scheduled = []
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    if "schedule:" in content or "cron:" in content:
                        scheduled.append(str(workflow.name))
                except:
                    pass
        
        state.scheduled_jobs = {
            "doc_health_jobs_found": scheduled,
            "gaps": "Limited scheduled documentation health checks found",
        }
        
        return state

    def _assess_overall_state(
        self, ssot_coverage: Dict, link_integrity: LinkIntegrity, automation_state: AutomationState
    ) -> OverallAssessment:
        """Assess overall documentation system state"""
        assessment = OverallAssessment()
        
        # Calculate metrics
        total_categories = ssot_coverage["total_categories"]
        found_categories = sum(
            1 for cat in ssot_coverage["categories"] 
            if cat["ssot_doc_found"]
        )
        ok_categories = sum(
            1 for cat in ssot_coverage["categories"] 
            if cat["status"] == "ok"
        )
        
        coverage_pct = (found_categories / total_categories * 100) if total_categories > 0 else 0
        ok_pct = (ok_categories / total_categories * 100) if total_categories > 0 else 0
        
        # Determine risk level
        if ok_pct >= 70:
            assessment.risk_level = "low"
        elif ok_pct >= 40:
            assessment.risk_level = "medium"
        else:
            assessment.risk_level = "high"
        
        # Summary
        assessment.summary = (
            f"Documentation system has {ok_categories}/{total_categories} SSOT categories "
            f"fully documented ({ok_pct:.0f}%). "
            f"Found {len(link_integrity.doc_ids.get('duplicates', []))} duplicate doc_ids. "
            f"Automation: {len(automation_state.validators['found'])} validators, "
            f"{len(automation_state.validators['wired_into_ci'])} wired to CI."
        )
        
        # Key findings
        assessment.key_findings = [
            f"SSOT coverage: {ok_categories}/{total_categories} categories have proper documentation",
            f"Total doc_ids found: {link_integrity.doc_ids.get('total_in_files', 0)}",
            f"Validators found: {len(automation_state.validators['found'])}",
            f"CI-integrated validators: {len(automation_state.validators['wired_into_ci'])}",
        ]
        
        # Recommendations
        recommendations = []
        
        if ok_pct < 50:
            recommendations.append({
                "priority": "high",
                "description": "Create SSOT documents for missing categories",
                "suggested_files": ["docs/ssot/phase_model.md", "docs/ssot/orchestrator_contract.md"],
            })
        
        if len(link_integrity.doc_ids.get('duplicates', [])) > 0:
            recommendations.append({
                "priority": "high",
                "description": "Resolve duplicate doc_ids",
                "suggested_files": [],
            })
        
        if len(automation_state.validators['not_wired']) > 5:
            recommendations.append({
                "priority": "medium",
                "description": "Wire validators into CI pipeline",
                "suggested_files": [".github/workflows/"],
            })
        
        assessment.recommended_next_actions = recommendations
        
        return assessment


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Analyze documentation system state per DOC-DOCS-SYSTEM-STATE-ANALYSIS-CLI-001"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root path (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON file path (default: stdout)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output",
    )
    
    args = parser.parse_args()
    
    # Validate repo root
    if not args.repo_root.is_dir():
        print(f"❌ Error: {args.repo_root} is not a directory", file=sys.stderr)
        sys.exit(1)
    
    # Run analysis
    print(f"📊 Documentation System Analysis")
    print(f"Repository: {args.repo_root}")
    print()
    
    analyzer = DocumentationAnalyzer(args.repo_root)
    report = analyzer.analyze()
    
    # Convert to dict
    report_dict = asdict(report)
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report_dict, f, indent=2)
        print(f"\n✅ Report saved to: {args.output}")
    else:
        print("\n" + "="*80)
        print(json.dumps(report_dict, indent=2))
    
    # Print summary
    print("\n" + "="*80)
    print("📋 SUMMARY")
    print("="*80)
    assessment = report.overall_assessment
    print(f"Overall: {assessment['summary']}")
    print(f"Risk Level: {assessment['risk_level'].upper()}")
    print(f"\nKey Findings:")
    for finding in assessment['key_findings']:
        print(f"  • {finding}")
    
    if assessment['recommended_next_actions']:
        print(f"\nRecommended Actions:")
        for action in assessment['recommended_next_actions']:
            print(f"  [{action['priority'].upper()}] {action['description']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
