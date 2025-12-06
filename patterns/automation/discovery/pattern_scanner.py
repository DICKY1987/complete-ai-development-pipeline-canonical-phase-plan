"""Auto-discovery layer for pattern detection and executor matching.

DOC_ID: DOC-PAT-DISCOVERY-PATTERN-SCANNER-001
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import yaml


class PatternScanner:
    def __init__(self, patterns_dir: Optional[Path] = None):
        self.patterns_dir = patterns_dir or Path(__file__).resolve().parents[2]
        self.specs_dir = self.patterns_dir / "specs"
        self.executors_dir = self.patterns_dir / "executors"
        self.registry_path = self.patterns_dir / "registry" / "PATTERN_INDEX.yaml"
    
    def scan_specs(self) -> List[Dict]:
        patterns = []
        if not self.specs_dir.exists():
            return patterns
        for spec_file in self.specs_dir.glob("*.pattern.yaml"):
            try:
                with open(spec_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data:
                        data["spec_file"] = spec_file.name
                        patterns.append(data)
            except Exception as e:
                print(f"Warning: Failed to load {spec_file}: {e}")
        return patterns
    
    def find_executor_for_pattern(self, pattern: Dict) -> Optional[str]:
        pattern_id = pattern.get("id") or pattern.get("pattern_id", "")
        if not pattern_id:
            return None
        if "executor" in pattern:
            executor_file = pattern["executor"]
            if not executor_file.endswith(".ps1"):
                executor_file += ".ps1"
            if (self.executors_dir / executor_file).exists():
                return executor_file
        base_name = pattern_id.lower().replace("pat-", "").replace("-", "_")
        candidates = [f"{base_name}_executor.ps1", f"{base_name}.ps1", f"{base_name}_001_executor.ps1"]
        for candidate in candidates:
            if (self.executors_dir / candidate).exists():
                return candidate
        return None
    
    def discover_and_update(self) -> Dict:
        patterns = self.scan_specs()
        return {"patterns_discovered": len(patterns), "timestamp": datetime.now().isoformat()}


def main():
    scanner = PatternScanner()
    result = scanner.discover_and_update()
    print(f"Patterns discovered: {result['patterns_discovered']}")


if __name__ == "__main__":
    main()
