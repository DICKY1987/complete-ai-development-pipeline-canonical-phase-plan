"""Cost and token tracking."""

from dataclasses import dataclass
from typing import Dict


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


class CostTracker:
    """Cost and API usage tracking."""
    
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
