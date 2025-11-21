"""Context window management and estimation."""

from typing import List
from pathlib import Path


class ContextEstimator:
    """Context window management."""
    
    TOKEN_PER_CHAR = 0.25  # Rough estimate: 4 chars per token
    
    def estimate_tokens(self, files: List[str], additional_context: str = "") -> int:
        """Estimate total token count for context."""
        total_chars = 0
        
        for f in files:
            try:
                total_chars += len(Path(f).read_text(encoding='utf-8'))
            except Exception:
                pass
        
        total_chars += len(additional_context)
        
        return int(total_chars * self.TOKEN_PER_CHAR)
