#!/usr/bin/env python3
"""Pattern Automation Monitoring Dashboard

Generates HTML dashboard showing:
- System health status
- Pattern detection metrics
- Execution trends
- Top patterns by usage
- Recent activity timeline
"""
# DOC_ID: DOC-PAT-MONITORING-DASHBOARD-002

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


class PatternDashboard:
    """Generate monitoring dashboard for pattern automation."""

    def __init__(self, patterns_dir: Path = None):
        if patterns_dir is None:
            patterns_dir = Path(__file__).resolve().parents[2]

        self.patterns_dir = patterns_dir
        self.db_path = patterns_dir / "metrics" / "pattern_automation.db"
        self.output_dir = patterns_dir / "reports" / "dashboard"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_dashboard(self) -> Path:
        """Generate complete HTML dashboard."""
        print("📊 Generating Pattern Automation Dashboard...")

        # Collect data
        metrics = self._collect_metrics()
        trends = self._calculate_trends()
        top_patterns = self._get_top_patterns()
        recent_activity = self._get_recent_activity()
        health_status = self._check_health()

        # Generate HTML
        html = self._render_html(
            metrics, trends, top_patterns, recent_activity, health_status
        )

        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"dashboard_{timestamp}.html"
        output_file.write_text(html, encoding="utf-8")

        # Create symlink to latest
        latest = self.output_dir / "latest.html"
        if latest.exists():
            latest.unlink()
        latest.write_text(html, encoding="utf-8")

        print(f"✅ Dashboard generated: {output_file}")
        print(f"🔗 Latest: {latest}")

        return output_file

    def _collect_metrics(self) -> Dict:
        """Collect key metrics from database."""
        if not self.db_path.exists():
            return {
                "total_executions": 0,
                "total_candidates": 0,
                "total_anti_patterns": 0,
                "success_rate": 0,
                "avg_time": 0,
            }

        db = sqlite3.connect(str(self.db_path))
        cursor = db.cursor()

        # Total counts
        total_exec = cursor.execute("SELECT COUNT(*) FROM execution_logs").fetchone()[0]
        total_cand = cursor.execute(
            "SELECT COUNT(*) FROM pattern_candidates"
        ).fetchone()[0]
        total_anti = cursor.execute("SELECT COUNT(*) FROM anti_patterns").fetchone()[0]

        # Success rate
        successful = cursor.execute(
            "SELECT COUNT(*) FROM execution_logs WHERE success = 1"
        ).fetchone()[0]
        success_rate = (successful / total_exec * 100) if total_exec > 0 else 0

        # Average execution time
        avg_time = (
            cursor.execute(
                "SELECT AVG(time_taken_seconds) FROM execution_logs"
            ).fetchone()[0]
            or 0
        )

        db.close()

        return {
            "total_executions": total_exec,
            "total_candidates": total_cand,
            "total_anti_patterns": total_anti,
            "success_rate": round(success_rate, 1),
            "avg_time": round(avg_time, 2),
        }

    def _calculate_trends(self) -> Dict:
        """Calculate 7-day trends."""
        if not self.db_path.exists():
            return {"7_day": []}

        db = sqlite3.connect(str(self.db_path))
        cursor = db.cursor()

        # Last 7 days
        seven_days = []
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            count = cursor.execute(
                "SELECT COUNT(*) FROM execution_logs WHERE DATE(timestamp) = ?", (date,)
            ).fetchone()[0]
            seven_days.append({"date": date, "count": count})

        db.close()

        return {"7_day": seven_days}

    def _get_top_patterns(self, limit: int = 10) -> List[Dict]:
        """Get most frequently executed patterns."""
        if not self.db_path.exists():
            return []

        db = sqlite3.connect(str(self.db_path))
        cursor = db.cursor()

        top = cursor.execute(
            """
            SELECT operation_kind, COUNT(*) as count,
                   AVG(time_taken_seconds) as avg_time,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
            FROM execution_logs
            GROUP BY operation_kind
            ORDER BY count DESC
            LIMIT ?
        """,
            (limit,),
        ).fetchall()

        db.close()

        return [
            {
                "pattern": row[0],
                "count": row[1],
                "avg_time": round(row[2], 2) if row[2] else 0,
                "success_rate": round(row[3], 1) if row[3] else 0,
            }
            for row in top
        ]

    def _get_recent_activity(self, limit: int = 20) -> List[Dict]:
        """Get recent executions."""
        if not self.db_path.exists():
            return []

        db = sqlite3.connect(str(self.db_path))
        cursor = db.cursor()

        recent = cursor.execute(
            """
            SELECT timestamp, operation_kind, success, time_taken_seconds
            FROM execution_logs
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (limit,),
        ).fetchall()

        db.close()

        return [
            {
                "timestamp": row[0],
                "pattern": row[1],
                "success": bool(row[2]),
                "time": round(row[3], 2) if row[3] else 0,
            }
            for row in recent
        ]

    def _check_health(self) -> Dict:
        """Check system health status."""
        issues = []
        status = "HEALTHY"

        if not self.db_path.exists():
            issues.append("Database not found")
            status = "CRITICAL"
        else:
            db = sqlite3.connect(str(self.db_path))
            cursor = db.cursor()

            recent = cursor.execute(
                "SELECT COUNT(*) FROM execution_logs WHERE timestamp > datetime('now', '-7 days')"
            ).fetchone()[0]

            if recent == 0:
                issues.append("No activity in last 7 days")
                status = "WARNING" if status != "CRITICAL" else status

            pending = cursor.execute(
                "SELECT COUNT(*) FROM pattern_candidates WHERE status = 'pending'"
            ).fetchone()[0]

            if pending > 10:
                issues.append(f"{pending} pattern candidates pending review")
                status = "WARNING" if status != "CRITICAL" else status

            db.close()

        return {"status": status, "issues": issues}

    def _render_html(
        self, metrics, trends, top_patterns, recent_activity, health
    ) -> str:
        """Render HTML dashboard."""
        status_colors = {
            "HEALTHY": "#28a745",
            "WARNING": "#ffc107",
            "CRITICAL": "#dc3545",
        }

        status_color = status_colors.get(health["status"], "#6c757d")

        chart_labels = json.dumps([d["date"] for d in trends["7_day"]])
        chart_data = json.dumps([d["count"] for d in trends["7_day"]])

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pattern Automation Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f5f7fa; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        header {{ background: white; padding: 30px; border-radius: 8px; margin-bottom: 20px;
                  box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .status {{ display: inline-block; padding: 6px 12px; border-radius: 4px;
                   background: {status_color}; color: white; font-weight: 600; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px; margin-bottom: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 8px;
                 box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .metric {{ font-size: 36px; font-weight: 700; color: #2c3e50; margin: 10px 0; }}
        .label {{ color: #7f8c8d; font-size: 14px; text-transform: uppercase;
                  letter-spacing: 0.5px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ecf0f1; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #495057; }}
        tr:hover {{ background: #f8f9fa; }}
        .success {{ color: #28a745; }}
        .failure {{ color: #dc3545; }}
        .timestamp {{ color: #6c757d; font-size: 12px; }}
        canvas {{ max-height: 300px; }}
        .issue {{ background: #fff3cd; border-left: 4px solid #ffc107;
                 padding: 12px; margin: 10px 0; border-radius: 4px; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <h1>Pattern Automation Dashboard</h1>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p style="margin-top: 10px;">
                <span class="status">{health['status']}</span>
            </p>
            {''.join(f'<div class="issue">⚠️  {issue}</div>' for issue in health['issues'])}
        </header>

        <div class="grid">
            <div class="card">
                <div class="label">Total Executions</div>
                <div class="metric">{metrics['total_executions']:,}</div>
            </div>
            <div class="card">
                <div class="label">Pattern Candidates</div>
                <div class="metric">{metrics['total_candidates']}</div>
            </div>
            <div class="card">
                <div class="label">Success Rate</div>
                <div class="metric">{metrics['success_rate']}%</div>
            </div>
            <div class="card">
                <div class="label">Avg Execution Time</div>
                <div class="metric">{metrics['avg_time']}s</div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 20px;">
            <h2 style="margin-bottom: 20px;">7-Day Execution Trend</h2>
            <canvas id="trendChart"></canvas>
        </div>

        <div class="grid" style="grid-template-columns: 1fr 1fr;">
            <div class="card">
                <h2 style="margin-bottom: 15px;">Top Patterns</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Pattern</th>
                            <th>Count</th>
                            <th>Avg Time</th>
                            <th>Success %</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f'''
                        <tr>
                            <td>{p['pattern']}</td>
                            <td>{p['count']}</td>
                            <td>{p['avg_time']}s</td>
                            <td>{p['success_rate']}%</td>
                        </tr>
                        ''' for p in top_patterns[:10])}
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2 style="margin-bottom: 15px;">Recent Activity</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Pattern</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f'''
                        <tr>
                            <td class="timestamp">{a['timestamp']}</td>
                            <td>{a['pattern']}</td>
                            <td class="{'success' if a['success'] else 'failure'}">
                                {'✅' if a['success'] else '❌'} {a['time']}s
                            </td>
                        </tr>
                        ''' for a in recent_activity[:15])}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('trendChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {chart_labels},
                datasets: [{{
                    label: 'Executions',
                    data: {chart_data},
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.3,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
        return html


def main():
    """Generate dashboard."""
    dashboard = PatternDashboard()
    output = dashboard.generate_dashboard()
    print(f"\n✨ Open in browser: file://{output.absolute()}")


if __name__ == "__main__":
    main()
