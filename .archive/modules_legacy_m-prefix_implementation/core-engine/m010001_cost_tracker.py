"""Cost and token tracking with UET compatibility."""

from dataclasses import dataclass
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timezone
import json
import sqlite3
from pathlib import Path

from modules.core_state import get_connection


@dataclass
class ModelPricing:
    model_name: str
    input_cost_per_1k: float
    output_cost_per_1k: float


PRICING_TABLE: Dict[str, ModelPricing] = {
    "gpt-4": ModelPricing("gpt-4", 0.03, 0.06),
    "gpt-3.5-turbo": ModelPricing("gpt-3.5-turbo", 0.0015, 0.002),
    "claude-3-opus": ModelPricing("claude-3-opus", 0.015, 0.075),
    "claude-3-sonnet": ModelPricing("claude-3-sonnet", 0.003, 0.015),
}


@dataclass
class UsageInfo:
    """Resource usage details for cost tracking."""
# DOC_ID: DOC-PAT-CORE-ENGINE-M010001-COST-TRACKER-493

    quantity: float
    unit: str
    rate: float

    @property
    def cost(self) -> float:
        return self.quantity * self.rate

    def to_dict(self) -> Dict[str, Any]:
        return {"quantity": self.quantity, "unit": self.unit, "rate": self.rate}


@dataclass
class CostBudget:
    """Cost budget configuration."""

    max_cost_usd: float
    warning_threshold: float = 0.8  # Warn at 80%
    enforcement_mode: str = "warn"  # 'warn', 'halt', 'continue'


class CostTracker:
    """Cost and API usage tracking (legacy + UET-compatible)."""

    VALID_RESOURCE_TYPES = {
        "api_call",
        "compute_time",
        "storage",
        "network",
        "tool_usage",
        "custom",
    }

    def __init__(self, db: Optional[Any] = None, budget: Optional[CostBudget] = None):
        self.db = db
        self.budget = budget

    def _get_conn(self) -> Tuple[sqlite3.Connection, bool]:
        """Return a connection and whether it should be closed by the caller."""
        if self.db is not None:
            if hasattr(self.db, "conn"):
                return self.db.conn, False
            if isinstance(self.db, sqlite3.Connection):
                return self.db, False
        conn = get_connection()
        return conn, True

    def _ensure_costs_table(self, conn: sqlite3.Connection) -> None:
        """Ensure the UET costs table exists for compatibility tests."""
        try:
            conn.execute("SELECT 1 FROM costs LIMIT 1")
            return
        except Exception:
            pass
        migration = Path("schema/migrations/005_add_costs_table.sql")
        if migration.exists():
            conn.executescript(migration.read_text(encoding="utf-8"))
            conn.commit()
            return
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS costs (
                cost_id TEXT PRIMARY KEY,
                execution_request_id TEXT,
                project_id TEXT,
                resource_type TEXT NOT NULL,
                resource_name TEXT,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                usage TEXT,
                recorded_at TEXT NOT NULL,
                metadata TEXT
            )
            """
        )
        conn.commit()

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        data = dict(row)
        for key in ("usage", "metadata"):
            if data.get(key):
                try:
                    data[key] = json.loads(data[key])
                except Exception:
                    pass
        return data

    def record_cost(
        self,
        cost_id: str,
        resource_type: str,
        amount: float,
        currency: str = "USD",
        execution_request_id: Optional[str] = None,
        project_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        usage: Optional[UsageInfo] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Record a cost entry using the UET-compatible schema."""
        if resource_type not in self.VALID_RESOURCE_TYPES:
            raise ValueError(f"Invalid resource_type: {resource_type}")
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        if len(currency) != 3 or not currency.isupper():
            raise ValueError("Currency must be 3-letter uppercase code")

        conn, should_close = self._get_conn()
        try:
            self._ensure_costs_table(conn)
            conn.execute(
                """
                INSERT INTO costs (
                    cost_id, execution_request_id, project_id, resource_type,
                    resource_name, amount, currency, usage, recorded_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cost_id,
                    execution_request_id,
                    project_id,
                    resource_type,
                    resource_name,
                    amount,
                    currency,
                    json.dumps(usage.to_dict()) if usage else None,
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps(metadata) if metadata else None,
                ),
            )
            conn.commit()
        finally:
            if should_close:
                conn.close()

        if self.budget:
            self._check_budget(cost_id, amount)
        return cost_id

    def get_cost(self, cost_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single cost entry if present."""
        conn, should_close = self._get_conn()
        try:
            self._ensure_costs_table(conn)
            row = conn.execute(
                "SELECT * FROM costs WHERE cost_id = ?", (cost_id,)
            ).fetchone()
            return self._row_to_dict(row) if row else None
        finally:
            if should_close:
                conn.close()

    def get_total_cost(self, run_id: str) -> float:
        """Total cost by run ID (prefers new costs table, falls back to legacy)."""
        conn, should_close = self._get_conn()
        try:
            try:
                self._ensure_costs_table(conn)
                row = conn.execute(
                    "SELECT SUM(amount) FROM costs WHERE execution_request_id = ?",
                    (run_id,),
                ).fetchone()
                if row and row[0] is not None:
                    return float(row[0])
            except Exception:
                pass
            cursor = conn.execute(
                "SELECT SUM(estimated_cost_usd) FROM cost_tracking WHERE run_id = ?",
                (run_id,),
            )
            result = cursor.fetchone()
            return float(result[0]) if result and result[0] else 0.0
        finally:
            if should_close:
                conn.close()

    def record_usage(
        self,
        run_id: str,
        workstream_id: str,
        step_id: str,
        worker_id: str,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Record token usage in the legacy cost_tracking table."""
        pricing = PRICING_TABLE.get(model_name, PRICING_TABLE["gpt-4"])
        cost = (
            (input_tokens / 1000.0) * pricing.input_cost_per_1k
            + (output_tokens / 1000.0) * pricing.output_cost_per_1k
        )

        conn, should_close = self._get_conn()
        try:
            conn.execute(
                """
                INSERT INTO cost_tracking
                (run_id, workstream_id, step_id, worker_id, input_tokens, output_tokens,
                 estimated_cost_usd, model_name, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
                (
                    run_id,
                    workstream_id,
                    step_id,
                    worker_id,
                    input_tokens,
                    output_tokens,
                    cost,
                    model_name,
                ),
            )
            conn.commit()
        finally:
            if should_close:
                conn.close()

        if self.budget:
            self._check_budget(run_id, cost)
        return cost

    def _check_budget(self, run_id: str, latest_cost: float) -> None:
        total_cost = self.get_total_cost(run_id)
        if not self.budget:
            return

        budget_usage = total_cost / self.budget.max_cost_usd
        if budget_usage >= self.budget.warning_threshold and budget_usage < 1.0:
            self._emit_budget_warning(run_id, total_cost, budget_usage)
        if budget_usage >= 1.0:
            self._handle_budget_exceeded(run_id, total_cost, budget_usage)

    def _emit_budget_warning(self, run_id: str, total_cost: float, usage: float) -> None:
        print(
            f"\nWARNING: Budget at {usage*100:.1f}% (${total_cost:.2f} / ${self.budget.max_cost_usd:.2f})"
        )

    def _handle_budget_exceeded(
        self, run_id: str, total_cost: float, usage: float
    ) -> None:
        if self.budget.enforcement_mode == "halt":
            raise BudgetExceededError(
                f"Budget exceeded: ${total_cost:.2f} / ${self.budget.max_cost_usd:.2f}"
            )
        if self.budget.enforcement_mode == "warn":
            print(
                f"\nBUDGET EXCEEDED: ${total_cost:.2f} / ${self.budget.max_cost_usd:.2f}"
            )

    def get_budget_status(self, run_id: str) -> Dict[str, Any]:
        total_cost = self.get_total_cost(run_id)
        if not self.budget:
            return {"total_cost_usd": total_cost, "budget_enabled": False}
        usage = total_cost / self.budget.max_cost_usd
        return {
            "total_cost_usd": total_cost,
            "budget_usd": self.budget.max_cost_usd,
            "remaining_usd": self.budget.max_cost_usd - total_cost,
            "usage_pct": usage * 100,
            "budget_enabled": True,
            "status": "exceeded"
            if usage >= 1.0
            else "warning"
            if usage >= self.budget.warning_threshold
            else "ok",
        }


class BudgetExceededError(Exception):
    """Raised when cost budget is exceeded in 'halt' mode."""

    pass


__all__ = ["CostTracker", "UsageInfo", "CostBudget", "ModelPricing", "PRICING_TABLE"]
