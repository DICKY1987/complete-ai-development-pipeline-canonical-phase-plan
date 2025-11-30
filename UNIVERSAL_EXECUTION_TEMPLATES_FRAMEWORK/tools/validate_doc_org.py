#!/usr/bin/env python3
"""
Documentation Organization Validator
Implements DOC-ORG-CHK-001 through DOC-ORG-CHK-006
"""
DOC_ID: DOC-SCRIPT-TOOLS-VALIDATE-DOC-ORG-356
DOC_ID: DOC-SCRIPT-TOOLS-VALIDATE-DOC-ORG-342
DOC_ID: DOC-PAT-TOOLS-VALIDATE-DOC-ORG-776
DOC_ID: DOC-PAT-TOOLS-VALIDATE-DOC-ORG-660
import argparse
import json
import jsonschema
import sys
from pathlib import Path


# DOC-ORG-023-SCHEMA: Inventory record schema
INVENTORY_SCHEMA = {
    "type": "object",
    "required": ["path", "name", "preview"],
    "properties": {
        "path": {"type": "string"},
        "name": {"type": "string"},
        "preview": {"type": "string"}
    },
    "additionalProperties": False
}

# DOC-ORG-033-SCHEMA: Move plan record schema
MOVE_PLAN_SCHEMA = {
    "type": "object",
    "required": ["path", "category", "target_dir", "reason"],
    "properties": {
        "path": {"type": "string"},
        "category": {
            "type": "string",
            "enum": ["spec", "planning", "scratch", "runtime", "archive", "ai", "unknown"]
        },
        "target_dir": {"type": ["string", "null"]},
        "reason": {"type": "string"}
    },
    "additionalProperties": False
}

ALLOWED_CATEGORIES = {"spec", "planning", "scratch", "runtime", "archive", "ai", "unknown"}


def validate_file(file_path: Path, schema_name: str) -> tuple[bool, str]:
    """Validate a JSONL file against a schema."""
    schema = INVENTORY_SCHEMA if schema_name == "inventory" else MOVE_PLAN_SCHEMA
    
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    try:
        line_num = 0
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line_num += 1
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    jsonschema.validate(record, schema)
                except json.JSONDecodeError as e:
                    return False, f"Line {line_num}: Invalid JSON: {e}"
                except jsonschema.ValidationError as e:
                    return False, f"Line {line_num}: Schema validation failed: {e.message}"
        
        return True, f"✅ {file_path.name} conforms to {schema_name} schema ({line_num} records)"
    except Exception as e:
        return False, f"Error reading file: {e}"


def check_categories(move_plan_path: Path) -> tuple[bool, str]:
    """Check that all category values are in allowed set."""
    invalid_categories = set()
    line_num = 0
    
    with move_plan_path.open("r", encoding="utf-8") as f:
        for line in f:
            line_num += 1
            if not line.strip():
                continue
            record = json.loads(line)
            category = record.get("category")
            if category not in ALLOWED_CATEGORIES:
                invalid_categories.add(category)
    
    if invalid_categories:
        return False, f"Invalid categories found: {invalid_categories}"
    return True, f"✅ All categories valid ({line_num} records)"


def check_unknown_moves(move_plan_path: Path) -> tuple[bool, str]:
    """Check that no moves are planned for unknown category."""
    unknown_moves = []
    
    with move_plan_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            if record["category"] == "unknown" and record.get("target_dir"):
                unknown_moves.append(record["path"])
    
    if unknown_moves:
        return False, f"Moves planned for unknown category: {len(unknown_moves)} files"
    return True, "✅ No moves planned for unknown category"


def check_target_dirs(move_plan_path: Path, docs_root: str = "docs/") -> tuple[bool, str]:
    """Check that all target directories are within docs/ root."""
    invalid_targets = []
    
    with move_plan_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            target_dir = record.get("target_dir")
            if target_dir and not target_dir.startswith(docs_root):
                invalid_targets.append((record["path"], target_dir))
    
    if invalid_targets:
        return False, f"Target dirs outside {docs_root}: {len(invalid_targets)} files"
    return True, f"✅ All target dirs within {docs_root}"


def main():
    parser = argparse.ArgumentParser(description="Validate documentation organization files")
    parser.add_argument("--file", help="File to validate")
    parser.add_argument("--schema", choices=["inventory", "move_plan"],
                       help="Schema to validate against")
    parser.add_argument("--check-categories", action="store_true",
                       help="Check category values in move plan")
    parser.add_argument("--check-unknown-moves", action="store_true",
                       help="Check for moves of unknown category")
    parser.add_argument("--check-target-dirs", action="store_true",
                       help="Check target directory paths")
    
    args = parser.parse_args()
    
    all_passed = True
    
    if args.file and args.schema:
        passed, msg = validate_file(Path(args.file), args.schema)
        print(msg)
        all_passed = all_passed and passed
    
    if args.check_categories:
        plan_path = Path(".state/docs/doc_move_plan.jsonl")
        passed, msg = check_categories(plan_path)
        print(msg)
        all_passed = all_passed and passed
    
    if args.check_unknown_moves:
        plan_path = Path(".state/docs/doc_move_plan.jsonl")
        passed, msg = check_unknown_moves(plan_path)
        print(msg)
        all_passed = all_passed and passed
    
    if args.check_target_dirs:
        plan_path = Path(".state/docs/doc_move_plan.jsonl")
        passed, msg = check_target_dirs(plan_path)
        print(msg)
        all_passed = all_passed and passed
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
