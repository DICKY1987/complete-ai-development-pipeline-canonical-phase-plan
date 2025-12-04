#!/usr/bin/env python3
"""Auto-approval workflow for high-confidence pattern candidates."""
# DOC_ID: DOC-PAT-LIFECYCLE-AUTO-APPROVAL-004

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import yaml


class AutoApprovalEngine:
    """Automatically approve high-confidence pattern candidates."""

    def __init__(self, patterns_dir: Path = None):
        if patterns_dir is None:
            patterns_dir = Path(__file__).resolve().parents[2]

        self.patterns_dir = patterns_dir
        self.db_path = patterns_dir / "metrics" / "pattern_automation.db"
        self.specs_dir = patterns_dir / "specs"
        self.registry_file = patterns_dir / "registry" / "PATTERN_INDEX.yaml"

        config_path = patterns_dir / "automation" / "config" / "detection_config.yaml"
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.auto_approve_enabled = self.config.get(
            "auto_approve_high_confidence", False
        )
        self.confidence_threshold = self.config.get("detection", {}).get(
            "auto_approval_confidence", 0.75
        )

        self.log_file = patterns_dir / "reports" / "auto_approval_log.jsonl"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def run_approval_cycle(self) -> Dict:
        """Run one approval cycle."""
        print("🔍 Auto-Approval Cycle Starting...")
        print(f"   Enabled: {self.auto_approve_enabled}")
        print(f"   Threshold: {self.confidence_threshold:.0%}")

        if not self.auto_approve_enabled:
            return {"approved": 0, "skipped": 0, "errors": []}

        results = {
            "timestamp": datetime.now().isoformat(),
            "approved": 0,
            "skipped": 0,
            "errors": [],
        }

        candidates = self._get_pending_candidates()
        print(f"   Found {len(candidates)} pending candidates")

        for candidate in candidates:
            try:
                if self._should_auto_approve(candidate):
                    print(f"   ✅ Auto-approving: {candidate['pattern_id']}")
                    self._approve_pattern(candidate)
                    results["approved"] += 1
                else:
                    results["skipped"] += 1
            except Exception as e:
                results["errors"].append(
                    f"Error approving {candidate['pattern_id']}: {e}"
                )

        self._log_approval_cycle(results)
        return results

    def _get_pending_candidates(self) -> List[Dict]:
        """Get pending pattern candidates."""
        if not self.db_path.exists():
            return []

        db = sqlite3.connect(str(self.db_path))
        cursor = db.cursor()

        rows = cursor.execute(
            """
            SELECT pattern_id, confidence, auto_generated_spec
            FROM pattern_candidates
            WHERE status = 'pending'
            ORDER BY confidence DESC
        """
        ).fetchall()

        db.close()

        return [{"pattern_id": r[0], "confidence": r[1], "spec": r[2]} for r in rows]

    def _should_auto_approve(self, candidate: Dict) -> bool:
        """Determine if candidate should be auto-approved."""
        return (
            candidate["confidence"] >= self.confidence_threshold and candidate["spec"]
        )

    def _approve_pattern(self, candidate: Dict):
        """Approve pattern."""
        pattern_id = candidate["pattern_id"]
        spec_file = self.specs_dir / f"{pattern_id}.pattern.yaml"
        spec_file.write_text(candidate["spec"], encoding="utf-8")

        db = sqlite3.connect(str(self.db_path))
        db.execute(
            """
            UPDATE pattern_candidates
            SET status = 'approved', updated_at = CURRENT_TIMESTAMP
            WHERE pattern_id = ?
        """,
            (pattern_id,),
        )
        db.commit()
        db.close()

    def _log_approval_cycle(self, results: Dict):
        """Log approval cycle results."""
        with open(self.log_file, "a") as f:
            f.write(json.dumps(results) + "\n")


if __name__ == "__main__":
    engine = AutoApprovalEngine()
    engine.run_approval_cycle()
