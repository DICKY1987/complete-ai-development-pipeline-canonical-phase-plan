"""
Analyze module centrality and importance in codebase.

Combines multiple metrics to determine module importance.
"""
# DOC_ID: DOC-CORE-AST-CENTRALITY-ANALYZER-207

from typing import Dict, List, Tuple
from pathlib import Path
from collections import defaultdict
import yaml

from .import_graph import ImportGraph
from .pagerank import PageRank


class CentralityAnalyzer:
    """
    Analyze module importance using multiple centrality metrics.
    
    Metrics:
    - PageRank: Importance based on import relationships
    - In-degree: Number of modules that import this module
    - Out-degree: Number of modules this module imports
    - Betweenness: How often module appears in dependency paths
    """
    
    def __init__(self, import_graph: ImportGraph):
        """
        Initialize centrality analyzer.
        
        Args:
            import_graph: ImportGraph instance
        """
        self.graph = import_graph
        self.pagerank = PageRank()
    
    def analyze(self) -> Dict[str, Dict[str, float]]:
        """
        Compute all centrality metrics for modules.
        
        Returns:
            Dict mapping module to metrics dict
        """
        metrics = {}
        
        # Get PageRank scores
        pagerank_scores = self.pagerank.compute(self.graph.adjacency)
        
        # Compute degree centrality
        in_degree = self._compute_in_degree()
        out_degree = self._compute_out_degree()
        
        # Combine metrics
        all_modules = self.graph.get_all_modules()
        for module in all_modules:
            metrics[module] = {
                "pagerank": pagerank_scores.get(module, 0.0),
                "in_degree": in_degree.get(module, 0),
                "out_degree": out_degree.get(module, 0),
                "total_degree": in_degree.get(module, 0) + out_degree.get(module, 0)
            }
        
        return metrics
    
    def _compute_in_degree(self) -> Dict[str, int]:
        """Compute in-degree (number of incoming imports)."""
        in_degree = defaultdict(int)
        for module, importers in self.graph.reverse_adjacency.items():
            in_degree[module] = len(importers)
        return dict(in_degree)
    
    def _compute_out_degree(self) -> Dict[str, int]:
        """Compute out-degree (number of outgoing imports)."""
        out_degree = defaultdict(int)
        for module, deps in self.graph.adjacency.items():
            out_degree[module] = len(deps)
        return dict(out_degree)
    
    def rank_modules(self, metric: str = "pagerank", top_n: int = None) -> List[Tuple[str, float]]:
        """
        Rank modules by specified metric.
        
        Args:
            metric: Metric to rank by (pagerank, in_degree, out_degree, total_degree)
            top_n: Return only top N modules
            
        Returns:
            List of (module, score) tuples sorted descending
        """
        metrics = self.analyze()
        
        if metric not in ["pagerank", "in_degree", "out_degree", "total_degree"]:
            raise ValueError(f"Unknown metric: {metric}")
        
        ranked = sorted(
            metrics.items(),
            key=lambda x: x[1][metric],
            reverse=True
        )
        
        results = [(module, data[metric]) for module, data in ranked]
        
        if top_n is not None:
            return results[:top_n]
        return results
    
    def identify_core_modules(self, threshold_percentile: float = 0.8) -> List[str]:
        """
        Identify core modules based on combined metrics.
        
        Args:
            threshold_percentile: Percentile threshold for core modules
            
        Returns:
            List of core module names
        """
        metrics = self.analyze()
        
        # Compute combined score (weighted average)
        combined_scores = {}
        for module, m in metrics.items():
            # Normalize and combine
            combined = (
                m["pagerank"] * 0.5 +  # PageRank weighted heavily
                (m["in_degree"] / max(1, max(metrics[mod]["in_degree"] for mod in metrics))) * 0.3 +
                (m["total_degree"] / max(1, max(metrics[mod]["total_degree"] for mod in metrics))) * 0.2
            )
            combined_scores[module] = combined
        
        # Find threshold
        scores = sorted(combined_scores.values(), reverse=True)
        if not scores:
            return []
        
        threshold_idx = int(len(scores) * (1 - threshold_percentile))
        threshold = scores[threshold_idx] if threshold_idx < len(scores) else scores[-1]
        
        # Return modules above threshold
        core_modules = [
            module for module, score in combined_scores.items()
            if score >= threshold
        ]
        
        return sorted(core_modules)
    
    def export_ranking(self, output_path: Path, metric: str = "pagerank", top_n: int = 50):
        """
        Export module ranking to YAML file.
        
        Args:
            output_path: Path to output file
            metric: Metric to rank by
            top_n: Number of top modules to include
        """
        ranked = self.rank_modules(metric, top_n)
        core_modules = self.identify_core_modules()
        
        data = {
            "metric": metric,
            "top_modules": [
                {
                    "rank": i + 1,
                    "module": module,
                    "score": round(score, 6),
                    "is_core": module in core_modules
                }
                for i, (module, score) in enumerate(ranked)
            ],
            "core_modules": core_modules,
            "statistics": {
                "total_modules": len(self.graph.get_all_modules()),
                "core_modules_count": len(core_modules),
                "core_percentage": round(len(core_modules) / max(1, len(self.graph.get_all_modules())) * 100, 1)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        print(f"Module ranking saved to: {output_path}")
        print(f"  Top {len(ranked)} modules by {metric}")
        print(f"  Core modules: {len(core_modules)}")


__all__ = ['CentralityAnalyzer']
