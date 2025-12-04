"""
PageRank algorithm for module importance ranking.

Ranks modules by centrality in the import graph.
"""

# DOC_ID: DOC-CORE-AST-PAGERANK-206

from collections import defaultdict
from typing import Dict, List, Tuple


class PageRank:
    """
    Compute PageRank scores for modules based on import relationships.

    Modules that are imported by many other modules get higher scores.
    """

    def __init__(
        self,
        damping_factor: float = 0.85,
        max_iterations: int = 100,
        tolerance: float = 1e-6,
    ):
        """
        Initialize PageRank calculator.

        Args:
            damping_factor: Probability of following a link (default: 0.85)
            max_iterations: Maximum number of iterations (default: 100)
            tolerance: Convergence threshold (default: 1e-6)
        """
        self.damping_factor = damping_factor
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def compute(self, adjacency: Dict[str, set]) -> Dict[str, float]:
        """
        Compute PageRank scores for modules.

        Args:
            adjacency: Dict mapping module to set of modules it imports

        Returns:
            Dict mapping module to PageRank score
        """
        # Get all nodes
        nodes = set(adjacency.keys())
        for deps in adjacency.values():
            nodes.update(deps)
        nodes = list(nodes)

        if not nodes:
            return {}

        # Initialize scores
        num_nodes = len(nodes)
        scores = {node: 1.0 / num_nodes for node in nodes}

        # Build reverse adjacency (who imports this module)
        reverse_adj = defaultdict(set)
        for node, deps in adjacency.items():
            for dep in deps:
                reverse_adj[dep].add(node)

        # Iterate until convergence
        for iteration in range(self.max_iterations):
            new_scores = {}
            max_diff = 0.0

            for node in nodes:
                # Base probability of random jump
                rank = (1 - self.damping_factor) / num_nodes

                # Add contributions from nodes that import this node
                for incoming_node in reverse_adj.get(node, []):
                    out_degree = len(adjacency.get(incoming_node, []))
                    if out_degree > 0:
                        rank += self.damping_factor * scores[incoming_node] / out_degree

                new_scores[node] = rank
                max_diff = max(max_diff, abs(new_scores[node] - scores[node]))

            scores = new_scores

            # Check convergence
            if max_diff < self.tolerance:
                break

        # Normalize scores to sum to 1.0
        total = sum(scores.values())
        if total > 0:
            scores = {node: score / total for node, score in scores.items()}

        return scores

    def rank_modules(
        self, adjacency: Dict[str, set], top_n: int = None
    ) -> List[Tuple[str, float]]:
        """
        Rank modules by PageRank score.

        Args:
            adjacency: Dict mapping module to set of modules it imports
            top_n: Return only top N modules (default: all)

        Returns:
            List of (module, score) tuples sorted by score descending
        """
        scores = self.compute(adjacency)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if top_n is not None:
            return ranked[:top_n]
        return ranked


__all__ = ["PageRank"]
