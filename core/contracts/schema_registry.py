"""Schema Version Registry - Manages versioned JSON schemas

DOC_ID: DOC-CORE-CONTRACTS-SCHEMA-REGISTRY-861
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from packaging import version


@dataclass
class SchemaInfo:
    """Schema metadata"""

    name: str
    version: str
    path: Path
    schema: Dict

    def __repr__(self) -> str:
        return f"SchemaInfo(name={self.name}, version={self.version})"


@dataclass
class CompatibilityResult:
    """Schema compatibility check result"""

    compatible: bool
    breaking_changes: List[str]
    warnings: List[str]

    def __repr__(self) -> str:
        status = "✅ Compatible" if self.compatible else "❌ Incompatible"
        return f"{status} ({len(self.breaking_changes)} breaking, {len(self.warnings)} warnings)"


class SchemaRegistry:
    """Central registry for all versioned schemas"""

    def __init__(self, schema_dir: Optional[Path] = None):
        """
        Initialize schema registry

        Args:
            schema_dir: Path to schema directory (defaults to repo_root/schema)
        """
        self.schema_dir = schema_dir or (Path.cwd() / "schema")
        self.schemas: Dict[str, Dict[str, SchemaInfo]] = {}
        self._load_schemas()

    def _load_schemas(self):
        """Scan and load all schemas from schema directory"""
        if not self.schema_dir.exists():
            raise FileNotFoundError(f"Schema directory not found: {self.schema_dir}")

        # Pattern: schema_name.vN.json
        pattern = re.compile(r"^(.+)\.(v\d+)\.json$")

        for schema_path in self.schema_dir.glob("*.json"):
            match = pattern.match(schema_path.name)
            if match:
                name, ver = match.groups()

                try:
                    with open(schema_path, "r", encoding="utf-8") as f:
                        schema = json.load(f)

                    # Validate schema format
                    if not isinstance(schema, dict):
                        print(f"Warning: Invalid schema format in {schema_path.name}")
                        continue

                    # Store schema
                    if name not in self.schemas:
                        self.schemas[name] = {}

                    self.schemas[name][ver] = SchemaInfo(
                        name=name, version=ver, path=schema_path, schema=schema
                    )

                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse {schema_path.name}: {e}")
                except Exception as e:
                    print(f"Warning: Error loading {schema_path.name}: {e}")

    def get_schema(self, name: str, ver: str = "v1") -> Optional[Dict]:
        """
        Get schema by name and version

        Args:
            name: Schema name (e.g., "execution_request")
            ver: Schema version (e.g., "v1")

        Returns:
            Schema dict or None if not found
        """
        schema_info = self.schemas.get(name, {}).get(ver)
        return schema_info.schema if schema_info else None

    def get_schema_info(self, name: str, ver: str = "v1") -> Optional[SchemaInfo]:
        """
        Get schema info by name and version

        Args:
            name: Schema name
            ver: Schema version

        Returns:
            SchemaInfo or None
        """
        return self.schemas.get(name, {}).get(ver)

    def get_latest_version(self, name: str) -> Optional[str]:
        """
        Get latest version for schema

        Args:
            name: Schema name

        Returns:
            Latest version string (e.g., "v2") or None
        """
        versions = self.schemas.get(name, {}).keys()
        if not versions:
            return None

        # Sort versions (v1, v2, v3, ...)
        sorted_versions = sorted(
            versions, key=lambda v: int(v[1:]) if v[1:].isdigit() else 0, reverse=True
        )
        return sorted_versions[0] if sorted_versions else None

    def list_schemas(self) -> List[SchemaInfo]:
        """
        List all available schemas

        Returns:
            List of SchemaInfo objects
        """
        all_schemas = []
        for name_dict in self.schemas.values():
            all_schemas.extend(name_dict.values())
        return sorted(all_schemas, key=lambda s: (s.name, s.version))

    def validate_compatibility(
        self, name: str, old_version: str, new_version: str
    ) -> CompatibilityResult:
        """
        Check if version upgrade is backward compatible

        Args:
            name: Schema name
            old_version: Old version (e.g., "v1")
            new_version: New version (e.g., "v2")

        Returns:
            CompatibilityResult with breaking changes and warnings
        """
        old_schema = self.get_schema(name, old_version)
        new_schema = self.get_schema(name, new_version)

        if not old_schema or not new_schema:
            return CompatibilityResult(
                compatible=False,
                breaking_changes=["Schema version not found"],
                warnings=[],
            )

        breaking_changes = []
        warnings = []

        # Check for removed required fields
        old_required = set(old_schema.get("required", []))
        new_required = set(new_schema.get("required", []))

        removed_required = old_required - new_required
        if removed_required:
            warnings.append(f"Removed required fields: {', '.join(removed_required)}")

        added_required = new_required - old_required
        if added_required:
            breaking_changes.append(
                f"Added required fields: {', '.join(added_required)}"
            )

        # Check for removed properties
        old_props = set(old_schema.get("properties", {}).keys())
        new_props = set(new_schema.get("properties", {}).keys())

        removed_props = old_props - new_props
        if removed_props:
            breaking_changes.append(f"Removed properties: {', '.join(removed_props)}")

        # Check for type changes
        for prop in old_props & new_props:
            old_type = old_schema["properties"][prop].get("type")
            new_type = new_schema["properties"][prop].get("type")

            if old_type != new_type:
                breaking_changes.append(
                    f"Changed type of '{prop}': {old_type} → {new_type}"
                )

        compatible = len(breaking_changes) == 0
        return CompatibilityResult(
            compatible=compatible,
            breaking_changes=breaking_changes,
            warnings=warnings,
        )

    def reload(self):
        """Reload all schemas from disk"""
        self.schemas.clear()
        self._load_schemas()

    def __repr__(self) -> str:
        schema_count = sum(len(versions) for versions in self.schemas.values())
        return f"SchemaRegistry(schemas={len(self.schemas)}, versions={schema_count})"
