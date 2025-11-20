"""Bootstrap Validation Engine - WS-02-03A"""
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
from jsonschema import validate, ValidationError, SchemaError

class BootstrapValidator:
    def __init__(self, project_profile_path: str, router_config_path: str, profile_id: str):
        """Load artifacts to validate"""
        self.project_profile_path = Path(project_profile_path)
        self.router_config_path = Path(router_config_path)
        self.profile_id = profile_id
        
        # Load artifacts
        with open(self.project_profile_path, 'r', encoding='utf-8') as f:
            self.project_profile = yaml.safe_load(f)
        
        with open(self.router_config_path, 'r', encoding='utf-8') as f:
            self.router_config = json.load(f)
        
        # Load schemas
        schema_dir = Path(__file__).parent.parent.parent / "schema"
        with open(schema_dir / "project_profile.v1.json", 'r', encoding='utf-8') as f:
            self.profile_schema = json.load(f)
        
        with open(schema_dir / "router_config.v1.json", 'r', encoding='utf-8') as f:
            self.router_schema = json.load(f)
        
        # Load referenced profile
        profiles_dir = Path(__file__).parent.parent.parent / "profiles"
        profile_path = profiles_dir / profile_id / "profile.json"
        if profile_path.exists():
            with open(profile_path, 'r', encoding='utf-8') as f:
                self.profile_def = json.load(f)
        else:
            self.profile_def = None
        
        # Tracking
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        self.auto_fixed: List[Dict] = []
        self.needs_human: List[Dict] = []
    
    def validate_all(self) -> Dict:
        """Run all validations"""
        self._validate_schemas()
        self._check_constraints()
        self._check_consistency()
        self._auto_fix_common_issues()
        
        return {
            "valid": len(self.errors) == 0 and len(self.needs_human) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "auto_fixed": self.auto_fixed,
            "needs_human": self.needs_human
        }
    
    def _validate_schemas(self):
        """Validate artifacts against JSON schemas"""
        # Validate PROJECT_PROFILE
        try:
            validate(self.project_profile, self.profile_schema)
        except ValidationError as e:
            self.errors.append({
                "type": "schema_validation",
                "artifact": "PROJECT_PROFILE.yaml",
                "message": e.message,
                "path": ".".join(str(p) for p in e.path),
                "validator": e.validator
            })
        except SchemaError as e:
            self.errors.append({
                "type": "schema_error",
                "artifact": "project_profile.v1.json",
                "message": str(e)
            })
        
        # Validate router_config
        try:
            validate(self.router_config, self.router_schema)
        except ValidationError as e:
            self.errors.append({
                "type": "schema_validation",
                "artifact": "router_config.json",
                "message": e.message,
                "path": ".".join(str(p) for p in e.path),
                "validator": e.validator
            })
        except SchemaError as e:
            self.errors.append({
                "type": "schema_error",
                "artifact": "router_config.v1.json",
                "message": str(e)
            })
    
    def _check_constraints(self):
        """Ensure constraints aren't relaxed beyond profile defaults"""
        if not self.profile_def:
            self.warnings.append({
                "type": "missing_profile",
                "message": f"Profile '{self.profile_id}' not found, skipping constraint checks"
            })
            return
        
        # Check max_lines_changed (example constraint)
        project_max = self.project_profile.get("constraints", {}).get("max_lines_changed")
        if project_max and project_max > 500:
            self.needs_human.append({
                "type": "relaxed_constraint",
                "constraint": "max_lines_changed",
                "profile_value": 500,
                "project_value": project_max,
                "message": f"Project relaxes max_lines_changed to {project_max} (profile default: 500)",
                "suggestion": "Reduce max_lines_changed to 500 or add justification"
            })
        
        # Check patch_only constraint
        project_patch = self.project_profile.get("constraints", {}).get("patch_only", True)
        if not project_patch:
            self.needs_human.append({
                "type": "relaxed_constraint",
                "constraint": "patch_only",
                "profile_value": True,
                "project_value": False,
                "message": "Project disables patch_only mode (allows direct file writes)",
                "suggestion": "Enable patch_only for safety or document exception"
            })
    
    def _check_consistency(self):
        """Check cross-artifact consistency"""
        # Check profile_id exists
        if self.project_profile.get("profile_id") != self.profile_id:
            self.errors.append({
                "type": "consistency_error",
                "message": f"Profile ID mismatch: expected '{self.profile_id}', got '{self.project_profile.get('profile_id')}'",
                "field": "profile_id"
            })
        
        # Check framework_paths are valid
        framework_paths = self.project_profile.get("framework_paths", {})
        project_root = Path(self.project_profile.get("project_root", "."))
        
        for path_name, path_value in framework_paths.items():
            if not path_value:
                continue
            full_path = project_root / path_value
            # Warn if path doesn't exist (may be created later)
            if not full_path.exists() and not path_name.endswith("_file"):
                self.warnings.append({
                    "type": "missing_path",
                    "path": path_value,
                    "message": f"Framework path '{path_name}' points to non-existent location: {path_value}"
                })
        
        # Check tools in router_config are in available_tools
        router_apps = set(self.router_config.get("apps", {}).keys())
        available_tool_ids = set(
            tool.get("tool_id") for tool in self.project_profile.get("available_tools", [])
            if isinstance(tool, dict)
        )
        
        missing_tools = router_apps - available_tool_ids
        if missing_tools:
            self.warnings.append({
                "type": "tool_mismatch",
                "message": f"Tools in router_config not listed in available_tools: {sorted(missing_tools)}",
                "suggestion": "Add missing tools to PROJECT_PROFILE.available_tools"
            })
    
    def _auto_fix_common_issues(self):
        """Auto-fix common issues where safe"""
        # Normalize paths (convert backslashes to forward slashes)
        fixed_paths = False
        framework_paths = self.project_profile.get("framework_paths", {})
        
        for key, value in framework_paths.items():
            if isinstance(value, str) and "\\" in value:
                normalized = value.replace("\\", "/")
                framework_paths[key] = normalized
                fixed_paths = True
        
        if fixed_paths:
            self.auto_fixed.append({
                "type": "path_normalization",
                "message": "Normalized Windows backslashes to forward slashes in framework_paths",
                "action": "Applied forward slash convention"
            })
            # Save fixed version
            with open(self.project_profile_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.project_profile, f, default_flow_style=False, sort_keys=False)
        
        # Add missing default values
        if "constraints" not in self.project_profile:
            self.project_profile["constraints"] = {"patch_only": True, "max_lines_changed": 500}
            self.auto_fixed.append({
                "type": "missing_defaults",
                "message": "Added default constraints",
                "action": "Set patch_only=True, max_lines_changed=500"
            })
            with open(self.project_profile_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.project_profile, f, default_flow_style=False, sort_keys=False)
        
        # Fix router_config defaults
        if "defaults" not in self.router_config:
            self.router_config["defaults"] = {"max_attempts": 3, "timeout_seconds": 600}
            self.auto_fixed.append({
                "type": "missing_defaults",
                "message": "Added default routing configuration",
                "action": "Set max_attempts=3, timeout_seconds=600"
            })
            with open(self.router_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.router_config, f, indent=2)


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python validator.py <project_profile.yaml> <router_config.json> <profile_id>")
        sys.exit(1)
    
    validator = BootstrapValidator(sys.argv[1], sys.argv[2], sys.argv[3])
    result = validator.validate_all()
    
    print(json.dumps(result, indent=2))
    
    # Exit with error code if validation failed
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
