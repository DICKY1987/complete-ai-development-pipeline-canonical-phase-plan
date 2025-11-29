import yaml
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timezone


class MigrationPlanner:
    def __init__(self, duplicate_registry: Dict, dependency_report: Dict):
        self.duplicates = duplicate_registry
        self.dependencies = dependency_report

    def create_plan(self) -> Dict:
        """Create ordered migration plan with batches."""

        print("?? Creating migration plan...")

        migration_order = self.dependencies["migration_order"]

        canonical_files = []
        for dup_info in self.duplicates["duplicates"].values():
            canonical = dup_info["canonical"]
            if canonical not in canonical_files:
                canonical_files.append(canonical)

        ordered_files = self._sort_by_dependencies(canonical_files, migration_order)

        batches = self._create_batches(ordered_files)

        return {
            "plan_date": datetime.now(timezone.utc).isoformat(),
            "total_files": len(ordered_files),
            "total_batches": len(batches),
            "execution_estimate_hours": len(batches) * 0.5,
            "batches": batches,
        }

    def _sort_by_dependencies(self, files: List[str], order: List[str]) -> List[str]:
        """Sort files according to dependency order."""
        file_order = {}
        for file_path in files:
            module_name = str(Path(file_path).with_suffix("")).replace("/", ".").replace(
                "\\", "."
            )
            file_order[module_name] = file_path

        sorted_files = []
        for module in order:
            if module in file_order:
                sorted_files.append(file_order[module])

        for file_path in files:
            if file_path not in sorted_files:
                sorted_files.append(file_path)

        return sorted_files

    def _create_batches(self, files: List[str]) -> List[Dict]:
        """Group files into migration batches by component."""

        components = {
            "core-state": [],
            "core-ast": [],
            "core-planning": [],
            "core-engine": [],
            "error-shared": [],
            "error-plugins": [],
            "error-engine": [],
            "aim": [],
            "pm": [],
            "specifications": [],
            "other": [],
        }

        for file_path in files:
            parts = Path(file_path).parts

            if "modules" in parts:
                idx = parts.index("modules")
                if idx + 1 < len(parts):
                    component_name = parts[idx + 1]
                    if component_name in components:
                        components[component_name].append(file_path)
                    else:
                        for comp in components:
                            if comp in component_name:
                                components[comp].append(file_path)
                                break
                        else:
                            components["other"].append(file_path)
            else:
                if "core" in parts:
                    if "state" in parts:
                        components["core-state"].append(file_path)
                    elif "ast" in parts:
                        components["core-ast"].append(file_path)
                    elif "planning" in parts:
                        components["core-planning"].append(file_path)
                    elif "engine" in parts:
                        components["core-engine"].append(file_path)
                    else:
                        components["other"].append(file_path)
                elif "error" in parts:
                    if "shared" in parts:
                        components["error-shared"].append(file_path)
                    elif "plugins" in parts:
                        components["error-plugins"].append(file_path)
                    elif "engine" in parts:
                        components["error-engine"].append(file_path)
                    else:
                        components["other"].append(file_path)
                elif "aim" in parts:
                    components["aim"].append(file_path)
                elif "pm" in parts:
                    components["pm"].append(file_path)
                elif "specifications" in parts:
                    components["specifications"].append(file_path)
                else:
                    components["other"].append(file_path)

        batches = []
        batch_num = 1

        for component, files in components.items():
            if not files:
                continue

            for i in range(0, len(files), 6):
                batch_files = files[i : i + 6]

                batches.append(
                    {
                        "batch_id": f"WS-{batch_num:03d}",
                        "component": component,
                        "files": batch_files,
                        "file_count": len(batch_files),
                        "status": "pending",
                        "dependencies": self._get_batch_dependencies(batch_num, batches),
                    }
                )

                batch_num += 1

        return batches

    def _get_batch_dependencies(self, current_batch: int, previous_batches: List[Dict]) -> List[str]:
        """Determine which previous batches this batch depends on."""
        if current_batch <= 1:
            return []
        else:
            return [previous_batches[-1]["batch_id"]]


if __name__ == "__main__":
    duplicates = yaml.safe_load(
        Path("UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/duplicate_registry.yaml").read_text()
    )

    dependencies = json.loads(
        Path("UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/dependency_report.json").read_text()
    )

    planner = MigrationPlanner(duplicates, dependencies)
    plan = planner.create_plan()

    print(f"\n? Migration plan created:")
    print(f"   - Total files: {plan['total_files']}")
    print(f"   - Total batches: {plan['total_batches']}")
    print(f"   - Est. execution time: {plan['execution_estimate_hours']:.1f} hours")

    print("\n?? Batches:")
    for batch in plan["batches"][:5]:
        deps = f" (depends on {', '.join(batch['dependencies'])})" if batch["dependencies"] else ""
        print(f"   - {batch['batch_id']}: {batch['component']} ({batch['file_count']} files){deps}")

    if len(plan["batches"]) > 5:
        print(f"   ... and {len(plan['batches']) - 5} more batches")

    output_path = Path("UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/migration_plan.yaml")
    output_path.write_text(yaml.dump(plan, default_flow_style=False))

    print(f"\n?? Plan saved: {output_path}")
