"""Pattern learner that extracts conventions from episodic memory entries."""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional

from .episodic_memory import Episode, EpisodicMemory


class PatternLearner:
    """Derives lightweight patterns from stored episodes."""
DOC_ID: DOC-CORE-MEMORY-PATTERN-LEARNER-616

    def __init__(self, memory: EpisodicMemory):
        self.memory = memory

    def learn_patterns(self, limit: int = 200) -> Dict[str, object]:
        episodes = self.memory.list_episodes(limit=limit)
        if not episodes:
            return {"conventions": [], "success_rate": None, "recent_examples": []}

        conventions_counter: Counter[str] = Counter()
        for episode in episodes:
            for convention in episode.project_conventions:
                normalized = convention.strip()
                if normalized:
                    conventions_counter[normalized] += 1

        success_rate = self._compute_success_rate(episodes)
        top_conventions = [name for name, _ in conventions_counter.most_common(5)]
        recent_examples = [self._episode_summary(ep) for ep in episodes[:3]]

        return {
            "conventions": top_conventions,
            "success_rate": success_rate,
            "recent_examples": recent_examples,
        }

    @staticmethod
    def _compute_success_rate(episodes: List[Episode]) -> Optional[float]:
        total = len(episodes)
        if total == 0:
            return None
        accepted = sum(1 for episode in episodes if episode.edit_accepted)
        return accepted / total

    @staticmethod
    def _episode_summary(episode: Episode) -> Dict[str, object]:
        return {
            "task_id": episode.task_id,
            "task_description": episode.task_description,
            "edit_accepted": episode.edit_accepted,
            "files_changed": episode.files_changed,
            "project_conventions": episode.project_conventions,
            "created_at": episode.created_at,
        }
