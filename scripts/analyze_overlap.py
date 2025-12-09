#!/usr/bin/env python3
"""
Analyze folder overlap and identify deprecated/redundant folders.
"""
import os
import json
from datetime import datetime

# Identified deprecated folders based on documentation
DEPRECATED_FOLDERS = {
    "src": "Deprecated - use core.*, error.* imports instead",
    "Module-Centric": "Documentation - migrated to docs/",
    "REFACTOR_2": "Planning docs - archived",
    "bring_back_docs_": "Recovery docs - should be in docs/",
    "ToDo_Task": "Sandbox/experimental - archive",
    "AI_SANDBOX": "Experimental - minimal content",
    "abstraction": "Old workstream generation - superseded by UET",
    "ai-logs-analyzer": "Feature service - verify if still needed",
}

UET_OVERLAPS = {
    "core": "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core",
    "error": "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error",
    "aim": "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/aim",
    "pm": "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/pm",
}


def analyze_folder(path):
    """Count files and check content type"""
    file_count = 0
    py_files = []
    md_files = []

    for root, dirs, files in os.walk(path):
        # Skip hidden and archived
        dirs[:] = [d for d in dirs if not d.startswith(".") and "archive" not in d]

        for f in files:
            if not f.startswith("."):
                file_count += 1
                full_path = os.path.join(root, f)
                if f.endswith(".py"):
                    py_files.append(full_path)
                elif f.endswith(".md"):
                    md_files.append(full_path)

    return {
        "total_files": file_count,
        "python_files": len(py_files),
        "markdown_files": len(md_files),
        "py_sample": py_files[:5],
        "md_sample": md_files[:5],
    }


def main():
    report = {
        "timestamp": datetime.now().isoformat(),
        "deprecated_folders": {},
        "uet_overlaps": {},
        "recommendations": {},
    }

    print("🔍 Analyzing deprecated folders...\n")

    for folder, reason in DEPRECATED_FOLDERS.items():
        if os.path.exists(folder):
            stats = analyze_folder(folder)
            report["deprecated_folders"][folder] = {
                "reason": reason,
                "stats": stats,
                "exists": True,
            }
            print(f"📁 {folder}/")
            print(f"   Reason: {reason}")
            print(f'   Files: {stats["total_files"]} total')
            print(
                f'   Python: {stats["python_files"]}, Markdown: {stats["markdown_files"]}'
            )
            print()

    print("\n🔄 Checking UET overlaps...\n")

    for old, new in UET_OVERLAPS.items():
        old_exists = os.path.exists(old)
        new_exists = os.path.exists(new)

        old_stats = analyze_folder(old) if old_exists else None
        new_stats = analyze_folder(new) if new_exists else None

        report["uet_overlaps"][old] = {
            "old_exists": old_exists,
            "old_stats": old_stats,
            "new_path": new,
            "new_exists": new_exists,
            "new_stats": new_stats,
            "status": "ALREADY_ARCHIVED" if not old_exists else "NEEDS_VERIFICATION",
        }

        status = "✅ Already archived" if not old_exists else "⚠️  Still exists"
        print(f"{old}/ → {new}/")
        print(f"   Status: {status}")
        if old_exists and old_stats:
            print(f'   Old: {old_stats["python_files"]} Python files')
        if new_exists and new_stats:
            print(f'   New: {new_stats["python_files"]} Python files')
        print()

    # Generate recommendations
    print("\n📋 RECOMMENDATIONS:\n")

    safe_to_archive = []
    needs_review = []

    for folder, info in report["deprecated_folders"].items():
        if info["stats"]["python_files"] == 0:
            safe_to_archive.append(folder)
            print(
                f'✅ SAFE TO ARCHIVE: {folder}/ (no Python code, {info["stats"]["total_files"]} files)'
            )
        else:
            needs_review.append(folder)
            print(
                f'⚠️  NEEDS REVIEW: {folder}/ ({info["stats"]["python_files"]} Python files)'
            )

    report["recommendations"] = {
        "safe_to_archive": safe_to_archive,
        "needs_review": needs_review,
    }

    # Save report
    report_file = "overlap_analysis_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Full report saved to: {report_file}")
    print("\n📊 Summary:")
    print(f'   Deprecated folders found: {len(report["deprecated_folders"])}')
    print(f"   Safe to archive: {len(safe_to_archive)}")
    print(f"   Need review: {len(needs_review)}")

    uet_archived = sum(
        1 for v in report["uet_overlaps"].values() if not v["old_exists"]
    )
    print(f"   UET overlaps already archived: {uet_archived}/{len(UET_OVERLAPS)}")


if __name__ == "__main__":
    main()
