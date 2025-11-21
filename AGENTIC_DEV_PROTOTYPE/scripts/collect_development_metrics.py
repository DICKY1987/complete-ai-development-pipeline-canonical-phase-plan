#!/usr/bin/env python3
"""
Development Metrics Collection Script
Collects all development data for analysis and optimization
Generated: 2025-11-20
"""

import json
import os
import glob
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import hashlib

class DevelopmentMetricsCollector:
    """Collects comprehensive development metrics from the project"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analytics_dir = self.project_root / "analytics"
        self.snapshot_dir = self.analytics_dir / "snapshots" / datetime.now().strftime("%Y-%m-%d")
        self.metrics = {
            "collection_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "execution_metrics": {},
            "code_metrics": {},
            "test_metrics": {},
            "specification_metrics": {},
            "ai_interaction_metrics": {},
            "git_metrics": {}
        }
    
    def collect_all_metrics(self):
        """Orchestrates collection of all metric types"""
        print("🔍 Starting comprehensive metrics collection...")
        
        self.collect_execution_metrics()
        self.collect_code_metrics()
        self.collect_test_metrics()
        self.collect_specification_metrics()
        self.collect_git_metrics()
        self.collect_file_inventory()
        
        self.save_metrics()
        self.generate_summary_report()
        
        print("✅ Metrics collection complete!")
        return self.metrics
    
    def collect_execution_metrics(self):
        """Collect phase execution timing and status"""
        print("📊 Collecting execution metrics...")
        
        # Collect from session reports
        session_files = list(self.project_root.glob("SESSION_*_FINAL_REPORT.md"))
        milestone_files = list(self.project_root.glob("MILESTONE_M*_SUMMARY.md"))
        
        self.metrics["execution_metrics"] = {
            "total_sessions": len(session_files),
            "completed_milestones": len(milestone_files),
            "session_files": [f.name for f in session_files],
            "milestone_files": [f.name for f in milestone_files]
        }
        
        # Parse master plan
        master_plan_path = self.project_root / "master_phase_plan.json"
        if master_plan_path.exists():
            with open(master_plan_path) as f:
                plan = json.load(f)
                self.metrics["execution_metrics"]["master_plan"] = {
                    "total_phases": len(plan.get("phases", [])),
                    "total_milestones": len(plan.get("milestones", [])),
                    "estimated_sequential_hours": plan.get("effort_estimates", {}).get("sequential", 0),
                    "estimated_parallel_hours": plan.get("effort_estimates", {}).get("with_parallelism", 0)
                }
        
        # Check ledger directory
        ledger_dir = self.project_root / "ledger"
        if ledger_dir.exists():
            ledger_files = list(ledger_dir.glob("*.json"))
            self.metrics["execution_metrics"]["ledger_entries"] = len(ledger_files)
    
    def collect_code_metrics(self):
        """Collect source code statistics"""
        print("💻 Collecting code metrics...")
        
        src_dir = self.project_root / "src"
        if not src_dir.exists():
            return
        
        python_files = list(src_dir.rglob("*.py"))
        
        total_lines = 0
        total_classes = 0
        total_functions = 0
        
        file_metrics = []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    file_info = {
                        "file": str(py_file.relative_to(self.project_root)),
                        "lines": len(lines),
                        "classes": content.count('class '),
                        "functions": content.count('def '),
                        "size_bytes": py_file.stat().st_size
                    }
                    
                    total_lines += file_info["lines"]
                    total_classes += file_info["classes"]
                    total_functions += file_info["functions"]
                    
                    file_metrics.append(file_info)
            except Exception as e:
                print(f"⚠️  Error reading {py_file}: {e}")
        
        self.metrics["code_metrics"] = {
            "total_python_files": len(python_files),
            "total_lines_of_code": total_lines,
            "total_classes": total_classes,
            "total_functions": total_functions,
            "average_lines_per_file": total_lines / len(python_files) if python_files else 0,
            "files": file_metrics
        }
    
    def collect_test_metrics(self):
        """Collect test coverage and results"""
        print("✅ Collecting test metrics...")
        
        tests_dir = self.project_root / "tests"
        if not tests_dir.exists():
            return
        
        test_files = list(tests_dir.rglob("test_*.py"))
        
        total_tests = 0
        test_file_info = []
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Count test functions
                    test_count = content.count('def test_')
                    total_tests += test_count
                    
                    test_file_info.append({
                        "file": str(test_file.relative_to(self.project_root)),
                        "test_functions": test_count,
                        "lines": len(content.split('\n'))
                    })
            except Exception as e:
                print(f"⚠️  Error reading {test_file}: {e}")
        
        self.metrics["test_metrics"] = {
            "total_test_files": len(test_files),
            "total_test_functions": total_tests,
            "test_files": test_file_info
        }
    
    def collect_specification_metrics(self):
        """Collect phase specification data"""
        print("📋 Collecting specification metrics...")
        
        phase_specs_dir = self.project_root / "phase_specs"
        if not phase_specs_dir.exists():
            return
        
        spec_files = list(phase_specs_dir.glob("*.json"))
        
        spec_details = []
        total_acceptance_criteria = 0
        total_dependencies = 0
        
        for spec_file in spec_files:
            try:
                with open(spec_file) as f:
                    spec = json.load(f)
                    
                    acceptance = len(spec.get("acceptance_criteria", []))
                    deps = len(spec.get("dependencies", []))
                    
                    total_acceptance_criteria += acceptance
                    total_dependencies += deps
                    
                    spec_details.append({
                        "file": spec_file.name,
                        "phase_id": spec.get("id", "unknown"),
                        "title": spec.get("title", "unknown"),
                        "acceptance_criteria_count": acceptance,
                        "dependencies_count": deps,
                        "estimated_hours": spec.get("effort_estimate", {}).get("hours", 0)
                    })
            except Exception as e:
                print(f"⚠️  Error reading {spec_file}: {e}")
        
        self.metrics["specification_metrics"] = {
            "total_phase_specs": len(spec_files),
            "total_acceptance_criteria": total_acceptance_criteria,
            "total_dependencies": total_dependencies,
            "specifications": spec_details
        }
    
    def collect_git_metrics(self):
        """Collect git repository statistics"""
        print("🔀 Collecting git metrics...")
        
        try:
            # Total commits
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            total_commits = int(result.stdout.strip()) if result.returncode == 0 else 0
            
            # Current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            current_branch = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            # File changes
            result = subprocess.run(
                ["git", "diff", "--shortstat"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            changes = result.stdout.strip() if result.returncode == 0 else "No changes"
            
            self.metrics["git_metrics"] = {
                "total_commits": total_commits,
                "current_branch": current_branch,
                "uncommitted_changes": changes,
                "git_available": True
            }
        except Exception as e:
            print(f"⚠️  Git metrics unavailable: {e}")
            self.metrics["git_metrics"] = {"git_available": False, "error": str(e)}
    
    def collect_file_inventory(self):
        """Create complete file inventory with checksums"""
        print("📁 Creating file inventory...")
        
        inventory = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip analytics and other large dirs
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'analytics']]
            
            for file in files:
                filepath = Path(root) / file
                try:
                    stat = filepath.stat()
                    
                    # Calculate checksum for small files
                    checksum = None
                    if stat.st_size < 1_000_000:  # Only hash files < 1MB
                        with open(filepath, 'rb') as f:
                            checksum = hashlib.md5(f.read()).hexdigest()
                    
                    inventory.append({
                        "path": str(filepath.relative_to(self.project_root)),
                        "size_bytes": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "checksum_md5": checksum
                    })
                except Exception as e:
                    print(f"⚠️  Error inventorying {filepath}: {e}")
        
        self.metrics["file_inventory"] = {
            "total_files": len(inventory),
            "files": inventory
        }
    
    def save_metrics(self):
        """Save collected metrics to JSON file"""
        metrics_file = self.analytics_dir / "metrics" / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        # Also save as latest
        latest_file = self.analytics_dir / "metrics" / "latest_metrics.json"
        with open(latest_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"💾 Metrics saved to: {metrics_file}")
    
    def generate_summary_report(self):
        """Generate human-readable summary report"""
        report_file = self.analytics_dir / "reports" / f"METRICS_SUMMARY_{datetime.now().strftime('%Y%m%d')}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Development Metrics Summary Report\n\n")
            f.write(f"**Generated:** {self.metrics['collection_timestamp']}\n\n")
            f.write("---\n\n")
            
            # Execution metrics
            f.write("## 📊 Execution Metrics\n\n")
            exec_m = self.metrics["execution_metrics"]
            f.write(f"- **Total Sessions:** {exec_m.get('total_sessions', 0)}\n")
            f.write(f"- **Completed Milestones:** {exec_m.get('completed_milestones', 0)}\n")
            if "master_plan" in exec_m:
                mp = exec_m["master_plan"]
                f.write(f"- **Total Phases:** {mp.get('total_phases', 0)}\n")
                f.write(f"- **Estimated Sequential Hours:** {mp.get('estimated_sequential_hours', 0)}\n")
                f.write(f"- **Estimated Parallel Hours:** {mp.get('estimated_parallel_hours', 0)}\n")
                time_saved = mp.get('estimated_sequential_hours', 0) - mp.get('estimated_parallel_hours', 0)
                seq_hours = mp.get('estimated_sequential_hours', 0)
                if seq_hours > 0:
                    f.write(f"- **Time Saved by Parallelism:** {time_saved} hours ({time_saved/seq_hours*100:.1f}%)\n")
            f.write("\n")
            
            # Code metrics
            f.write("## 💻 Code Metrics\n\n")
            code_m = self.metrics["code_metrics"]
            f.write(f"- **Total Python Files:** {code_m.get('total_python_files', 0)}\n")
            f.write(f"- **Total Lines of Code:** {code_m.get('total_lines_of_code', 0)}\n")
            f.write(f"- **Total Classes:** {code_m.get('total_classes', 0)}\n")
            f.write(f"- **Total Functions:** {code_m.get('total_functions', 0)}\n")
            f.write(f"- **Average Lines/File:** {code_m.get('average_lines_per_file', 0):.1f}\n")
            f.write("\n")
            
            # Test metrics
            f.write("## ✅ Test Metrics\n\n")
            test_m = self.metrics["test_metrics"]
            f.write(f"- **Total Test Files:** {test_m.get('total_test_files', 0)}\n")
            f.write(f"- **Total Test Functions:** {test_m.get('total_test_functions', 0)}\n")
            code_files = code_m.get('total_python_files', 1)
            test_files = test_m.get('total_test_files', 0)
            f.write(f"- **Test/Code Ratio:** {test_files/code_files:.2f}\n")
            f.write("\n")
            
            # Specification metrics
            f.write("## 📋 Specification Metrics\n\n")
            spec_m = self.metrics["specification_metrics"]
            f.write(f"- **Total Phase Specs:** {spec_m.get('total_phase_specs', 0)}\n")
            f.write(f"- **Total Acceptance Criteria:** {spec_m.get('total_acceptance_criteria', 0)}\n")
            f.write(f"- **Total Dependencies:** {spec_m.get('total_dependencies', 0)}\n")
            f.write("\n")
            
            # Git metrics
            f.write("## 🔀 Git Metrics\n\n")
            git_m = self.metrics["git_metrics"]
            if git_m.get("git_available"):
                f.write(f"- **Total Commits:** {git_m.get('total_commits', 0)}\n")
                f.write(f"- **Current Branch:** {git_m.get('current_branch', 'unknown')}\n")
                f.write(f"- **Uncommitted Changes:** {git_m.get('uncommitted_changes', 'unknown')}\n")
            else:
                f.write("- Git metrics unavailable\n")
            f.write("\n")
            
            # File inventory
            f.write("## 📁 File Inventory\n\n")
            inv = self.metrics["file_inventory"]
            f.write(f"- **Total Files:** {inv.get('total_files', 0)}\n")
            total_size = sum(f.get('size_bytes', 0) for f in inv.get('files', []))
            f.write(f"- **Total Size:** {total_size / 1024:.1f} KB\n")
            f.write("\n")
        
        print(f"📄 Summary report saved to: {report_file}")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    
    collector = DevelopmentMetricsCollector(str(project_root))
    metrics = collector.collect_all_metrics()
    
    print("\n" + "="*60)
    print("✨ Metrics Collection Complete!")
    print("="*60)
    print(f"\n📊 Collected {len(metrics)} metric categories")
    print(f"💾 Data saved to: {collector.analytics_dir / 'metrics'}")
    print(f"📄 Report saved to: {collector.analytics_dir / 'reports'}")
    print("\n✅ Ready for analysis and optimization!")


if __name__ == "__main__":
    main()
