"""
RAPTOR hierarchical indexing (levels 0-4) using a simple summarizer.
"""

# DOC_ID: DOC-CORE-INDEXING-RAPTOR-503

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List

from core.indexing.summarizer import Summarizer


class RaptorLevel(int, Enum):
    LEVEL0 = 0  # raw chunks
    LEVEL1 = 1  # function summaries
    LEVEL2 = 2  # file summaries
    LEVEL3 = 3  # module summaries
    LEVEL4 = 4  # system summary


@dataclass
class RaptorNode:
    level: RaptorLevel
    key: str
    summary: str
    children: List[str]


class RaptorIndexer:
    """Minimal RAPTOR pipeline."""

    def __init__(self, summarizer: Summarizer, output_dir: Path):
        self.summarizer = summarizer
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build(self, repo_map: Dict) -> Dict[str, int]:
        """
        Build hierarchical summaries from repository map.

        Returns counts per level.
        """
        modules = repo_map.get("modules", {})
        level_nodes: Dict[RaptorLevel, List[RaptorNode]] = {
            lvl: [] for lvl in RaptorLevel
        }

        # Level 0/1: functions/classes summaries from signatures
        for module_name, module_info in modules.items():
            file_path = module_info.get("file", "")
            funcs = module_info.get("functions", [])
            classes = module_info.get("classes", [])

            for func in funcs:
                key = f"{module_name}.{func.get('name','')}"
                summary = self._summarize_signature(func)
                level_nodes[RaptorLevel.LEVEL1].append(
                    RaptorNode(RaptorLevel.LEVEL1, key, summary, [])
                )
                level_nodes[RaptorLevel.LEVEL0].append(
                    RaptorNode(RaptorLevel.LEVEL0, key, summary, [])
                )

            for cls in classes:
                key = f"{module_name}.{cls.get('name','')}"
                summary = self._summarize_class_signature(cls)
                level_nodes[RaptorLevel.LEVEL1].append(
                    RaptorNode(RaptorLevel.LEVEL1, key, summary, [])
                )
                level_nodes[RaptorLevel.LEVEL0].append(
                    RaptorNode(RaptorLevel.LEVEL0, key, summary, [])
                )

            # Level 2: file summary
            func_summaries = [
                n.summary
                for n in level_nodes[RaptorLevel.LEVEL1]
                if n.key.startswith(module_name)
            ]
            file_summary = self.summarizer.summarize([file_path] + func_summaries)
            level_nodes[RaptorLevel.LEVEL2].append(
                RaptorNode(
                    RaptorLevel.LEVEL2,
                    file_path,
                    file_summary,
                    [
                        n.key
                        for n in level_nodes[RaptorLevel.LEVEL1]
                        if n.key.startswith(module_name)
                    ],
                )
            )

        # Level 3: module summaries (per module)
        for module_name in modules.keys():
            child_keys = [
                n.key
                for n in level_nodes[RaptorLevel.LEVEL2]
                if n.key.startswith(module_name.split(".")[0])
            ]
            child_summaries = [
                n.summary
                for n in level_nodes[RaptorLevel.LEVEL2]
                if n.key in child_keys
            ]
            module_summary = self.summarizer.summarize([module_name] + child_summaries)
            level_nodes[RaptorLevel.LEVEL3].append(
                RaptorNode(RaptorLevel.LEVEL3, module_name, module_summary, child_keys)
            )

        # Level 4: system summary
        system_summary = self.summarizer.summarize(
            [n.summary for n in level_nodes[RaptorLevel.LEVEL3]]
        )
        level_nodes[RaptorLevel.LEVEL4].append(
            RaptorNode(
                RaptorLevel.LEVEL4,
                "system",
                system_summary,
                [n.key for n in level_nodes[RaptorLevel.LEVEL3]],
            )
        )

        self._write(level_nodes)

        return {f"level_{lvl.value}": len(nodes) for lvl, nodes in level_nodes.items()}

    def _summarize_signature(self, sig: Dict) -> str:
        name = sig.get("name", "")
        params = ", ".join(sig.get("params", []))
        return f"{name}({params})"

    def _summarize_class_signature(self, sig: Dict) -> str:
        name = sig.get("name", "")
        bases = ", ".join(sig.get("bases", []))
        return f"class {name}({bases})"

    def _write(self, level_nodes: Dict[RaptorLevel, List[RaptorNode]]):
        """Persist summaries as JSONL per level."""
        import json

        for level, nodes in level_nodes.items():
            out_file = self.output_dir / f"raptor_level_{level.value}.jsonl"
            with out_file.open("w", encoding="utf-8") as f:
                for node in nodes:
                    f.write(
                        json.dumps(
                            {
                                "level": node.level.value,
                                "key": node.key,
                                "summary": node.summary,
                                "children": node.children,
                            }
                        )
                        + "\n"
                    )


__all__ = ["RaptorIndexer", "RaptorLevel", "RaptorNode"]
