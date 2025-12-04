# DOC_LINK: DOC-TEST-INDEXING-TEST-RAPTOR-306
from pathlib import Path

from core.indexing.raptor import RaptorIndexer
from core.indexing.summarizer import Summarizer


def test_raptor_build(tmp_path):
    repo_map = {
        "modules": {
            "pkg.mod": {
                "file": "pkg/mod.py",
                "functions": [
                    {
                        "name": "foo",
                        "params": ["x"],
                        "return_type": None,
                        "is_async": False,
                        "decorators": [],
                    }
                ],
                "classes": [
                    {"name": "Bar", "bases": [], "methods": [], "decorators": []}
                ],
            }
        }
    }
    idx = RaptorIndexer(Summarizer(max_len=128), output_dir=tmp_path)
    counts = idx.build(repo_map)
    assert counts["level_0"] >= 2
    assert counts["level_4"] == 1
    assert (tmp_path / "raptor_level_4.jsonl").exists()
