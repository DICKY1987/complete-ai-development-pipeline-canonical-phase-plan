"""Doc Suite Auto-Generator
Automatically generates complete 8-file doc suites for pattern specs.

TRIGGERS:
1. New pattern spec created in specs/ without doc suite
2. Scheduled task (nightly): Find incomplete patterns
3. Manual: python doc_suite_generator.py --pattern-id PAT-XYZ-001

GENERATES:
- Registry entry (PATTERN_INDEX.yaml)
- Schema file (.schema.json)
- Schema sidecar (.schema.id.yaml)
- Executor script (.ps1 or .py)
- Test file (test_*.ps1)
- 3 Example instances (.json)
"""
DOC_ID: DOC-PAT-GENERATORS-DOC-SUITE-GENERATOR-887

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys


class DocSuiteGenerator:
    """Generates complete 8-file doc suites for patterns."""
    
    def __init__(self, patterns_dir: Path):
        self.patterns_dir = patterns_dir
        self.specs_dir = patterns_dir / "specs"
        self.schemas_dir = patterns_dir / "schemas"
        self.executors_dir = patterns_dir / "executors"
        self.tests_dir = patterns_dir / "tests"
        self.examples_dir = patterns_dir / "examples"
        self.registry_file = patterns_dir / "registry" / "PATTERN_INDEX.yaml"
        
    def find_incomplete_patterns(self) -> List[Dict]:
        """Find pattern specs missing doc suite files."""
        incomplete = []
        
        if not self.specs_dir.exists():
            return incomplete
            
        for spec_file in self.specs_dir.glob("*.pattern.yaml"):
            pattern_id = self._extract_pattern_id(spec_file)
            if not pattern_id:
                continue
                
            missing = self._check_missing_files(pattern_id)
            if missing:
                incomplete.append({
                    'pattern_id': pattern_id,
                    'spec_file': str(spec_file),
                    'missing_files': missing
                })
        
        return incomplete
    
    def _extract_pattern_id(self, spec_file: Path) -> Optional[str]:
        """Extract pattern_id from spec file."""
        try:
            with open(spec_file, 'r', encoding='utf-8') as f:
                spec = yaml.safe_load(f)
                return spec.get('pattern_id')
        except Exception as e:
            print(f"[WARN] Failed to read {spec_file.name}: {e}")
            return None
    
    def _check_missing_files(self, pattern_id: str) -> List[str]:
        """Check which doc suite files are missing."""
        pattern_name = pattern_id.lower().replace('pat-', '').replace('-', '_')
        
        required_files = {
            'registry': self.registry_file,
            'schema': self.schemas_dir / f"{pattern_name}.schema.json",
            'schema_sidecar': self.schemas_dir / f"{pattern_name}.schema.id.yaml",
            'executor': self.executors_dir / f"{pattern_name}_executor.ps1",
            'test': self.tests_dir / f"test_{pattern_name}_executor.ps1",
            'example_minimal': self.examples_dir / pattern_name / "instance_minimal.json",
            'example_full': self.examples_dir / pattern_name / "instance_full.json",
            'example_test': self.examples_dir / pattern_name / "instance_test.json",
        }
        
        missing = []
        for file_type, file_path in required_files.items():
            if file_type == 'registry':
                # Check if pattern is in registry
                if not self._pattern_in_registry(pattern_id):
                    missing.append(file_type)
            elif not file_path.exists():
                missing.append(file_type)
        
        return missing
    
    def _pattern_in_registry(self, pattern_id: str) -> bool:
        """Check if pattern is registered in PATTERN_INDEX.yaml."""
        if not self.registry_file.exists():
            return False
        
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = yaml.safe_load(f) or {}
                patterns = registry.get('patterns', [])
                return any(p.get('pattern_id') == pattern_id for p in patterns)
        except Exception:
            return False
    
    def generate_doc_suite(self, pattern_id: str, spec_file: Path) -> Dict:
        """Generate all missing doc suite files for a pattern."""
        print(f"\n[GEN] Generating doc suite for {pattern_id}...")
        
        # Read spec
        with open(spec_file, 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f)
        
        pattern_name = pattern_id.lower().replace('pat-', '').replace('-', '_')
        doc_id = spec.get('doc_id', f"DOC-{pattern_id}")
        
        generated = []
        
        # Only generate missing files
        missing = self._check_missing_files(pattern_id)
        
        if 'schema' in missing:
            schema_file = self.schemas_dir / f"{pattern_name}.schema.json"
            self._generate_schema(spec, schema_file)
            generated.append(str(schema_file))
        
        if 'schema_sidecar' in missing:
            sidecar_file = self.schemas_dir / f"{pattern_name}.schema.id.yaml"
            self._generate_schema_sidecar(spec, sidecar_file, doc_id)
            generated.append(str(sidecar_file))
        
        if 'executor' in missing:
            executor_file = self.executors_dir / f"{pattern_name}_executor.ps1"
            self._generate_executor(spec, executor_file)
            generated.append(str(executor_file))
        
        if 'test' in missing:
            test_file = self.tests_dir / f"test_{pattern_name}_executor.ps1"
            self._generate_test(spec, test_file)
            generated.append(str(test_file))
        
        # Generate examples
        examples_dir = self.examples_dir / pattern_name
        for example_type in ['minimal', 'full', 'test']:
            if f'example_{example_type}' in missing:
                examples_dir.mkdir(parents=True, exist_ok=True)
                example_file = examples_dir / f"instance_{example_type}.json"
                self._generate_example(spec, example_file, example_type)
                generated.append(str(example_file))
        
        if 'registry' in missing:
            self._add_to_registry(spec, pattern_id, doc_id)
            generated.append('registry_entry')
        
        print(f"[OK] Generated {len(generated)} files for {pattern_id}")
        return {
            'pattern_id': pattern_id,
            'doc_id': doc_id,
            'files_generated': generated,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_schema(self, spec: Dict, schema_file: Path):
        """Generate JSON schema from spec."""
        schema_file.parent.mkdir(parents=True, exist_ok=True)
        
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": spec.get('name', 'Pattern'),
            "description": spec.get('intent', spec.get('description', '')),
            "type": "object",
            "properties": spec.get('inputs', {}),
            "required": [k for k, v in spec.get('inputs', {}).items() if v.get('required', False)]
        }
        
        with open(schema_file, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2)
        
        print(f"  [OK] Schema: {schema_file.name}")
    
    def _generate_schema_sidecar(self, spec: Dict, sidecar_file: Path, doc_id: str):
        """Generate schema ID sidecar."""
        sidecar_file.parent.mkdir(parents=True, exist_ok=True)
        
        sidecar = {
            'doc_id': doc_id,
            'pattern_id': spec.get('pattern_id'),
            'schema_version': '1.0.0',
            'generated_at': datetime.now().isoformat()
        }
        
        with open(sidecar_file, 'w', encoding='utf-8') as f:
            yaml.dump(sidecar, f, default_flow_style=False)
        
        print(f"  [OK] Sidecar: {sidecar_file.name}")
    
    def _generate_executor(self, spec: Dict, executor_file: Path):
        """Generate PowerShell executor stub."""
        executor_file.parent.mkdir(parents=True, exist_ok=True)
        
        executor_content = f"""# Pattern Executor: {spec.get('name')}
# Pattern ID: {spec.get('pattern_id')}
# Auto-generated: {datetime.now().isoformat()}

param(
    [Parameter(Mandatory=$true)]
    [string]$InstanceFile
)

$ErrorActionPreference = "Stop"

# Read instance
$instance = Get-Content $InstanceFile -Raw | ConvertFrom-Json

Write-Host "[EXEC] Running {spec.get('name')}..." -ForegroundColor Cyan

# TODO: Implement execution logic based on spec
# Inputs: {', '.join(spec.get('inputs', {}).keys())}

Write-Host "[OK] Execution complete" -ForegroundColor Green
"""
        
        with open(executor_file, 'w', encoding='utf-8') as f:
            f.write(executor_content)
        
        print(f"  [OK] Executor: {executor_file.name}")
    
    def _generate_test(self, spec: Dict, test_file: Path):
        """Generate Pester test stub."""
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        test_content = f"""# Tests for: {spec.get('name')}
# Pattern ID: {spec.get('pattern_id')}
# Auto-generated: {datetime.now().isoformat()}

Describe "{spec.get('name')} Executor Tests" {{
    It "Loads and validates minimal instance" {{
        # Test with minimal example
        $result = # TODO: Call executor
        $result | Should -Not -BeNullOrEmpty
    }}
    
    It "Executes successfully with full instance" {{
        # Test with full example
        $result = # TODO: Call executor
        $result | Should -Not -BeNullOrEmpty
    }}
}}
"""
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"  [OK] Test: {test_file.name}")
    
    def _generate_example(self, spec: Dict, example_file: Path, example_type: str):
        """Generate example instance JSON."""
        example_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Build example based on inputs
        inputs = spec.get('inputs', {})
        example = {}
        
        for input_name, input_spec in inputs.items():
            if example_type == 'minimal' and not input_spec.get('required', False):
                continue
            
            # Generate sample value
            input_type = input_spec.get('type', 'string')
            if input_type == 'string':
                example[input_name] = input_spec.get('example', f'example_{input_name}')
            elif input_type == 'integer':
                example[input_name] = input_spec.get('default', 1)
            elif input_type == 'boolean':
                example[input_name] = input_spec.get('default', True)
            elif input_type == 'array':
                example[input_name] = input_spec.get('default', [])
            elif input_type == 'object':
                example[input_name] = input_spec.get('default', {})
        
        with open(example_file, 'w', encoding='utf-8') as f:
            json.dump(example, f, indent=2)
        
        print(f"  [OK] Example ({example_type}): {example_file.name}")
    
    def _add_to_registry(self, spec: Dict, pattern_id: str, doc_id: str):
        """Add pattern to PATTERN_INDEX.yaml."""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = yaml.safe_load(f) or {}
        else:
            registry = {'patterns': []}
        
        registry['patterns'].append({
            'pattern_id': pattern_id,
            'doc_id': doc_id,
            'name': spec.get('name'),
            'category': spec.get('category'),
            'status': spec.get('status', 'active'),
            'auto_generated': True,
            'created_at': datetime.now().isoformat()
        })
        
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            yaml.dump(registry, f, default_flow_style=False, sort_keys=False)
        
        print(f"  [OK] Registry: Added {pattern_id}")


def main():
    """Main entry point."""
    patterns_dir = Path(__file__).parent.parent.parent
    generator = DocSuiteGenerator(patterns_dir)
    
    print("=" * 80)
    print("DOC SUITE AUTO-GENERATOR")
    print("=" * 80)
    
    print("\n[SCAN] Scanning for incomplete patterns...")
    incomplete = generator.find_incomplete_patterns()
    
    if not incomplete:
        print("[OK] All patterns have complete doc suites")
        return 0
    
    print(f"[FOUND] {len(incomplete)} patterns missing doc suite files\n")
    
    results = []
    for pattern in incomplete:
        spec_file = Path(pattern['spec_file'])
        result = generator.generate_doc_suite(pattern['pattern_id'], spec_file)
        results.append(result)
    
    print("\n" + "=" * 80)
    print("[DONE] DOC SUITE GENERATION COMPLETE")
    print("=" * 80)
    print(f"\n[STATS] Patterns processed: {len(results)}")
    total_files = sum(len(r['files_generated']) for r in results)
    print(f"[STATS] Files generated: {total_files}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
