# DOC_LINK: DOC-CORE-ENGINE-PATCH-MANAGER-083
from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class PatchArtifact:
    patch_id: str
    run_id: str
    ws_id: str
    step_name: str
    attempt: int
    patch_file: Path
    diff_hash: str
    files_modified: List[str]
    line_count: int
    hunks: int
    additions: int
    deletions: int


@dataclass
class PatchParseResult:
    files_modified: List[str]
    hunks: int
    additions: int
    deletions: int
    line_count: int


@dataclass
class ApplyResult:
    success: bool
    message: str
    files_modified: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)


class PatchManager:
    def __init__(self, ledger_path: str):
        self.ledger_path = Path(ledger_path)
        self.ledger_path.mkdir(parents=True, exist_ok=True)

    def parse_patch_content(self, content: str) -> PatchParseResult:
        files: List[str] = []
        hunks = 0
        additions = 0
        deletions = 0
        line_count = 0
        for line in content.splitlines():
            if line.startswith("+++ b/"):
                target = line[6:].split("\t", 1)[0]
                if target not in files:
                    files.append(target)
            elif line.startswith("@@"):
                hunks += 1
            elif line.startswith("+++ ") or line.startswith("--- "):
                continue
            elif line.startswith("+"):
                additions += 1
                line_count += 1
            elif line.startswith("-"):
                deletions += 1
                line_count += 1
        return PatchParseResult(
            files_modified=files,
            hunks=hunks,
            additions=additions,
            deletions=deletions,
            line_count=line_count,
        )

    def parse_patch(self, patch_path: Path) -> PatchParseResult:
        content = patch_path.read_text(encoding="utf-8")
        return self.parse_patch_content(content)

    def capture_patch(
        self,
        *,
        run_id: str,
        ws_id: str,
        worktree_path: str,
        step_name: Optional[str] = None,
        attempt: int = 1,
    ) -> PatchArtifact:
        step = step_name or "step"
        patch_id = f"{ws_id}-{run_id}-{step}-{attempt}"
        patch_file = self.ledger_path / f"{patch_id}.patch"
        result = subprocess.run(
            ["git", "-C", worktree_path, "diff", "--patch"],
            capture_output=True,
            text=True,
        )
        content = result.stdout
        patch_file.write_text(content, encoding="utf-8")
        stats = self.parse_patch_content(content)
        diff_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return PatchArtifact(
            patch_id=patch_id,
            run_id=run_id,
            ws_id=ws_id,
            step_name=step,
            attempt=attempt,
            patch_file=patch_file,
            diff_hash=diff_hash,
            files_modified=stats.files_modified,
            line_count=stats.line_count,
            hunks=stats.hunks,
            additions=stats.additions,
            deletions=stats.deletions,
        )

    def get_patch_stats(self, patch_file: Path) -> Dict[str, int | List[str] | str]:
        stats = self.parse_patch(patch_file)
        content = patch_file.read_text(encoding="utf-8")
        diff_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return {
            "files_modified": stats.files_modified,
            "file_count": len(stats.files_modified),
            "hunks": stats.hunks,
            "additions": stats.additions,
            "deletions": stats.deletions,
            "line_count": stats.line_count,
            "diff_hash": diff_hash,
            "size_bytes": len(content.encode("utf-8")),
        }

    def apply_patch(self, patch_file: Path, repo_path: str, *, dry_run: bool = False) -> ApplyResult:
        command = ["git", "-C", repo_path, "apply"]
        if dry_run:
            command.append("--check")
        command.append(str(patch_file))
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            parse_result = self.parse_patch(patch_file)
            message = "dry run succeeded" if dry_run else "Patch applied successfully"
            return ApplyResult(
                success=True,
                message=message,
                files_modified=parse_result.files_modified,
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr or ""
            conflicts = ["conflict" for _ in range(stderr.count("conflict"))] if "conflict" in stderr.lower() else []
            return ApplyResult(
                success=False,
                message=stderr.strip() or str(exc),
                errors=[stderr.strip()] if stderr.strip() else [str(exc)],
                conflicts=conflicts,
            )

    def reverse_patch(self, patch_file: Path, repo_path: str) -> ApplyResult:
        command = ["git", "-C", repo_path, "apply", "-R", str(patch_file)]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            return ApplyResult(success=True, message="Patch reversed successfully")
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr or ""
            return ApplyResult(success=False, message=stderr.strip() or str(exc))


__all__ = [
    "PatchManager",
    "PatchArtifact",
    "PatchParseResult",
    "ApplyResult",
]
