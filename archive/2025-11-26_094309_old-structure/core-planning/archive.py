# DOC_LINK: DOC-PAT-CORE-PLANNING-ARCHIVE-406
from __future__ import annotations

import shutil
from pathlib import Path


def auto_archive(path: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / (path.name + ".zip")
    if out.exists():
        out.unlink()
    shutil.make_archive(str(out.with_suffix("")), "zip", path)
    return out

