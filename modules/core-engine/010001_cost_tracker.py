"""Cost and token tracking.

Phase I WS-I6: Enhanced with budget enforcement.
"""

from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime, timezone


@dataclass
class ModelPricing:
    model_name: str
    input_cost_per_1k: float
    output_cost_per_1k: float


PRICING_TABLE: Dict[str, ModelPricing] = {
    'gpt-4': ModelPricing('gpt-4', 0.03, 0.06),
    'gpt-3.5-turbo': ModelPricing('gpt-3.5-turbo', 0.0015, 0.002),
    'claude-3-opus': ModelPricing('claude-3-opus', 0.015, 0.075),
    'claude-3-sonnet': ModelPricing('claude-3-sonnet', 0.003, 0.015),
}


@dataclass
class CostBudget:
    """Cost budget configuration."""
    max_cost_usd: float
    warning_threshold: float = 0.8  # Warn at 80%
    enforcement_mode: str = 'warn'  # 'warn', 'halt', 'continue'


class CostTracker:
    """Cost and API usage tracking."""
    
    def __init__(self, budget: Optional[CostBudget] = None):
        """Initialize cost tracker.
        
        Args:
            budget: Optional cost budget configuration
        """
        self.budget = budget
    
    def record_usage(
        self,
        run_id: str,
        workstream_id: str,
        step_id: str,
        worker_id: str,
        model_name: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Record token usage and calculate cost."""
        from core.state.db import get_connection
        
        pricing = PRICING_TABLE.get(model_name, PRICING_TABLE['gpt-4'])
        
        cost = (
            (input_tokens / 1000.0) * pricing.input_cost_per_1k +
            (output_tokens / 1000.0) * pricing.output_cost_per_1k
        )
        
        conn = get_connection()
        try:
            conn.execute("""
                INSERT INTO cost_tracking
                (run_id, workstream_id, step_id, worker_id, input_tokens, output_tokens, 
                 estimated_cost_usd, model_name, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (run_id, workstream_id, step_id, worker_id, input_tokens, output_tokens, cost, model_name))
            conn.commit()
        finally:
            conn.close()
        
        # Check budget after recording
        if self.budget:
            self._check_budget(run_id, cost)
        
        return cost
    
    def get_total_cost(self, run_id: str) -> float:
        """Get total cost for a run."""
        from core.state.db import get_connection
        
        conn = get_connection()
        try:
            cursor = conn.execute(
                "SELECT SUM(estimated_cost_usd) FROM cost_tracking WHERE run_id = ?",
                (run_id,)
            )
            result = cursor.fetchone()
            return result[0] if result and result[0] else 0.0
        finally:
            conn.close()
    
    def _check_budget(self, run_id: str, latest_cost: float) -> None:
        """Check if budget is exceeded.
        
        Args:
            run_id: Run ID
            latest_cost: Latest cost added
        """
        total_cost = self.get_total_cost(run_id)
        
        if not self.budget:
            return
        
        budget_usage = total_cost / self.budget.max_cost_usd
        
        # Warning threshold
        if budget_usage >= self.budget.warning_threshold and budget_usage < 1.0:
            self._emit_budget_warning(run_id, total_cost, budget_usage)
        
        # Budget exceeded
        if budget_usage >= 1.0:
            self._handle_budget_exceeded(run_id, total_cost, budget_usage)
    
    def _emit_budget_warning(self, run_id: str, total_cost: float, usage: float) -> None:
        """Emit budget warning event."""
        from core.state import db
        
        db.record_event(
            event_type='budget_warning',
            run_id=run_id,
            payload={
                'total_cost_usd': total_cost,
                'budget_usd': self.budget.max_cost_usd,
                'usage_pct': usage * 100
            }
        )
        
        print(f"\n⚠️  WARNING: Budget at {usage*100:.1f}% (${total_cost:.2f} / ${self.budget.max_cost_usd:.2f})")
    
    def _handle_budget_exceeded(self, run_id: str, total_cost: float, usage: float) -> None:
        """Handle budget exceeded scenario.
        
        Args:
            run_id: Run ID
            total_cost: Total cost
            usage: Budget usage fraction
        """
        from core.state import db
        
        db.record_event(
            event_type='budget_exceeded',
            run_id=run_id,
            payload={
                'total_cost_usd': total_cost,
                'budget_usd': self.budget.max_cost_usd,
                'usage_pct': usage * 100,
                'enforcement_mode': self.budget.enforcement_mode
            }
        )
        
        if self.budget.enforcement_mode == 'halt':
            raise BudgetExceededError(
                f"Budget exceeded: ${total_cost:.2f} / ${self.budget.max_cost_usd:.2f}"
            )
        elif self.budget.enforcement_mode == 'warn':
            print(f"\n🛑 BUDGET EXCEEDED: ${total_cost:.2f} / ${self.budget.max_cost_usd:.2f}")
            print("   (continuing due to 'warn' mode)")
    
    def get_budget_status(self, run_id: str) -> Dict[str, any]:
        """Get current budget status.
        
        Args:
            run_id: Run ID
            
        Returns:
            Budget status dictionary
        """
        total_cost = self.get_total_cost(run_id)
        
        if not self.budget:
            return {
                'total_cost_usd': total_cost,
                'budget_enabled': False
            }
        
        usage = total_cost / self.budget.max_cost_usd
        
        return {
            'total_cost_usd': total_cost,
            'budget_usd': self.budget.max_cost_usd,
            'remaining_usd': self.budget.max_cost_usd - total_cost,
            'usage_pct': usage * 100,
            'budget_enabled': True,
            'status': 'exceeded' if usage >= 1.0 else 'warning' if usage >= self.budget.warning_threshold else 'ok'
        }


class BudgetExceededError(Exception):
    """Raised when cost budget is exceeded in 'halt' mode."""
    pass
