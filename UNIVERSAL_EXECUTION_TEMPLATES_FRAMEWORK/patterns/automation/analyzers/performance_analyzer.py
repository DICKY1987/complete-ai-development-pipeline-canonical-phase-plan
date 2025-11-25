"""Pattern Performance Analyzer (AUTO-004)

Generate weekly reports on pattern usage and effectiveness.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List


class PatternPerformanceAnalyzer:
    """Generate insights from pattern execution data."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.report_dir = Path(__file__).parent.parent.parent / "reports" / "weekly"
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_weekly_report(self) -> str:
        """Generate comprehensive weekly performance report."""
        report_data = {
            'top_patterns': self._rank_by_usage(),
            'time_saved': self._calculate_total_savings(),
            'underused_patterns': self._find_underused(),
            'new_pattern_candidates': self._detect_manual_work(),
            'anti_patterns': self._detect_failures()
        }
        
        # Generate markdown report
        report_md = self._format_report(report_data)
        
        # Save report
        report_file = self.report_dir / f"report-{datetime.now().strftime('%Y-W%W')}.md"
        report_file.write_text(report_md, encoding='utf-8')
        
        # Update pattern index with metrics
        self._update_pattern_index(report_data)
        
        return str(report_file)
    
    def _rank_by_usage(self) -> List[Dict]:
        """Rank patterns by usage in last 7 days."""
        cursor = self.db.execute(
            """
            SELECT pattern_id, COUNT(*) as uses, 
                   SUM(time_taken_seconds) as total_time,
                   AVG(time_taken_seconds) as avg_time,
                   SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes
            FROM execution_logs
            WHERE timestamp >= datetime('now', '-7 days')
              AND pattern_id IS NOT NULL
            GROUP BY pattern_id
            ORDER BY uses DESC
            LIMIT 10
            """
        )
        
        patterns = []
        for row in cursor.fetchall():
            time_saved = (row[3] * 0.6 * row[1]) / 60  # Assume 60% time savings
            patterns.append({
                'pattern_id': row[0],
                'uses': row[1],
                'hours_saved': time_saved / 60,
                'success_rate': row[4] / row[1] if row[1] > 0 else 0
            })
        
        return patterns
    
    def _calculate_total_savings(self) -> Dict:
        """Calculate total time saved by all patterns."""
        cursor = self.db.execute(
            """
            SELECT COUNT(*) as total_executions,
                   SUM(time_taken_seconds) as total_time,
                   SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes
            FROM execution_logs
            WHERE timestamp >= datetime('now', '-7 days')
              AND pattern_id IS NOT NULL
            """
        )
        
        row = cursor.fetchone()
        if not row:
            return {'hours_saved': 0, 'executions': 0}
        
        # Assume pattern saves 60% vs manual
        total_seconds = row[1] or 0
        estimated_manual_seconds = total_seconds / 0.4
        saved_seconds = estimated_manual_seconds - total_seconds
        
        return {
            'hours_saved': saved_seconds / 3600,
            'executions': row[0],
            'success_rate': row[2] / row[0] if row[0] > 0 else 0
        }
    
    def _find_underused(self) -> List[str]:
        """Find patterns that haven't been used recently."""
        cursor = self.db.execute(
            """
            SELECT pattern_id, last_used
            FROM pattern_metrics
            WHERE last_used IS NULL 
               OR last_used < datetime('now', '-30 days')
            ORDER BY last_used ASC
            LIMIT 5
            """
        )
        
        return [row[0] for row in cursor.fetchall()]
    
    def _detect_manual_work(self) -> List[Dict]:
        """Detect manual work that could be automated."""
        # Look for executions without pattern_id
        cursor = self.db.execute(
            """
            SELECT operation_kind, COUNT(*) as count
            FROM execution_logs
            WHERE timestamp >= datetime('now', '-7 days')
              AND pattern_id IS NULL
            GROUP BY operation_kind
            HAVING count >= 3
            ORDER BY count DESC
            """
        )
        
        candidates = []
        for row in cursor.fetchall():
            candidates.append({
                'operation_kind': row[0],
                'manual_count': row[1],
                'suggestion': f'Consider creating pattern for {row[0]}'
            })
        
        return candidates
    
    def _detect_failures(self) -> List[Dict]:
        """Detect recurring failures (anti-patterns)."""
        cursor = self.db.execute(
            """
            SELECT pattern_id, COUNT(*) as failures,
                   COUNT(*) * 100.0 / (
                       SELECT COUNT(*) FROM execution_logs e2 
                       WHERE e2.pattern_id = e1.pattern_id
                   ) as failure_rate
            FROM execution_logs e1
            WHERE timestamp >= datetime('now', '-7 days')
              AND success = 0
              AND pattern_id IS NOT NULL
            GROUP BY pattern_id
            HAVING failure_rate > 40
            ORDER BY failures DESC
            """
        )
        
        failures = []
        for row in cursor.fetchall():
            failures.append({
                'pattern_id': row[0],
                'failures': row[1],
                'failure_rate': row[2]
            })
        
        return failures
    
    def _format_report(self, data: Dict) -> str:
        """Format report as markdown."""
        now = datetime.now()
        week_num = now.isocalendar()[1]
        
        md = f"""# Pattern Usage Report - Week {week_num} {now.year}
Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}

---

## 🏆 Top Patterns (by usage)

"""
        
        for i, pattern in enumerate(data['top_patterns'], 1):
            md += f"{i}. **{pattern['pattern_id']}**: {pattern['uses']} uses, "
            md += f"{pattern['hours_saved']:.1f} hours saved "
            md += f"({pattern['success_rate']:.0%} success rate)\n"
        
        md += f"""
---

## 📊 Weekly Summary

- **Total Executions**: {data['time_saved']['executions']}
- **Total Time Saved**: {data['time_saved']['hours_saved']:.1f} hours
- **Overall Success Rate**: {data['time_saved']['success_rate']:.1%}

---

## 📈 New Pattern Candidates

"""
        
        if data['new_pattern_candidates']:
            for candidate in data['new_pattern_candidates']:
                md += f"- **{candidate['operation_kind']}**: {candidate['manual_count']} manual executions detected\n"
                md += f"  → {candidate['suggestion']}\n\n"
        else:
            md += "*No new pattern candidates detected this week.*\n"
        
        md += "\n---\n\n## ⚠️ Anti-Patterns Detected\n\n"
        
        if data['anti_patterns']:
            for anti in data['anti_patterns']:
                md += f"- **{anti['pattern_id']}**: {anti['failures']} failures "
                md += f"({anti['failure_rate']:.1f}% failure rate)\n"
                md += f"  → **Recommendation**: Review and improve pattern\n\n"
        else:
            md += "*No high-failure patterns detected this week.*\n"
        
        md += "\n---\n\n## 📉 Underused Patterns\n\n"
        
        if data['underused_patterns']:
            for pattern_id in data['underused_patterns']:
                md += f"- {pattern_id}\n"
        else:
            md += "*All patterns are actively used.*\n"
        
        md += "\n---\n\n## 🔧 Recommended Actions\n\n"
        
        actions = []
        if data['new_pattern_candidates']:
            actions.append(f"1. Create {len(data['new_pattern_candidates'])} new patterns for manual work")
        if data['anti_patterns']:
            actions.append(f"2. Fix {len(data['anti_patterns'])} high-failure patterns")
        if data['underused_patterns']:
            actions.append(f"3. Review {len(data['underused_patterns'])} underused patterns")
        
        if actions:
            md += '\n'.join(actions)
        else:
            md += "*No critical actions required this week.*\n"
        
        return md
    
    def _update_pattern_index(self, data: Dict):
        """Update PATTERN_INDEX.yaml with latest metrics."""
        # This would update the registry with usage stats
        pass
