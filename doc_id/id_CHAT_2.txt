Here’s a concrete starting point you can actually drop into your repo and wire up.

---

## 1. `id_coordinator.py` – Concrete Python Module

```python
"""
id_coordinator.py

Centralized doc_id assignment and inventory updates for orchestrated,
multi-worktree execution.

This module is intentionally small and generic:

- It does NOT know how your registry is implemented.
- It does NOT touch worktrees.
- It ONLY:
  - coordinates doc_id assignment via a callback, and
  - keeps docs_inventory.jsonl in sync.

You should:
- Provide a mint_func that calls your real doc_id registry CLI / library.
- Call IDCoordinator.assign_doc_id() from your orchestrator/worktree layer.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Optional, Any


MintFunc = Callable[[str, Optional[str]], str]
InventoryEntry = Dict[str, Any]


@dataclass
class IDCoordinator:
    """
    Centralized doc_id assignment for orchestrated execution.

    Invariants:
    - For a given file_path (in MAIN, not worktree), only ONE doc_id is minted.
    - All assignment flows through this class, not directly from worktrees.
    - docs_inventory.jsonl is updated incrementally as IDs are assigned.
    """

    inventory_path: Path
    mint_func: MintFunc

    _lock: threading.RLock = field(default_factory=threading.RLock, init=False, repr=False)
    _assigned_by_path: Dict[str, str] = field(default_factory=dict, init=False, repr=False)

    def assign_doc_id(self, file_path: str, module_id: Optional[str] = None) -> str:
        """
        Return a stable doc_id for the given file_path.

        - file_path MUST be the path in the main working tree (e.g. 'core/state/db.py'),
          NOT a worktree-specific path.
        - If a doc_id was already assigned for this path in this process, it is reused.
        - Otherwise, mint_func is called to generate a new doc_id, and the inventory is updated.
        """
        norm_path = self._normalize_path(file_path)

        with self._lock:
            if norm_path in self._assigned_by_path:
                return self._assigned_by_path[norm_path]

            doc_id = self.mint_func(norm_path, module_id)
            if not isinstance(doc_id, str) or not doc_id:
                raise ValueError(f"mint_func returned invalid doc_id for {norm_path!r}: {doc_id!r}")

            self._assigned_by_path[norm_path] = doc_id
            self._update_inventory(norm_path, doc_id, module_id)
            return doc_id

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #

    def _normalize_path(self, file_path: str) -> str:
        """
        Normalize paths to a consistent, POSIX-style string relative to repo root.
        """
        return str(Path(file_path).as_posix())

    def _update_inventory(self, file_path: str, doc_id: str, module_id: Optional[str]) -> None:
        """
        Update docs_inventory.jsonl with the given doc_id for file_path.

        - If an entry for file_path exists, it is updated in-place.
        - Otherwise, a new entry is appended.
        - This method is intentionally simple and robust rather than hyper-optimized.
        """
        inv_path = self.inventory_path

        # Load existing inventory (if any)
        entries: Dict[str, InventoryEntry] = {}
        if inv_path.exists():
            with inv_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    path_key = entry.get("path")
                    if isinstance(path_key, str):
                        entries[path_key] = entry

        # Upsert entry for this path
        now = datetime.now(timezone.utc).isoformat()
        entry = entries.get(file_path, {})
        entry["path"] = file_path
        entry["doc_id"] = doc_id
        entry.setdefault("module_id", module_id)
        entry["last_assigned_at"] = now
        entry["last_assigned_by"] = "IDCoordinator"

        # Only overwrite module_id if we were explicitly given one
        if module_id is not None:
            entry["module_id"] = module_id

        entries[file_path] = entry

        # Write back as JSONL
        with inv_path.open("w", encoding="utf-8") as f:
            for e in entries.values():
                f.write(json.dumps(e, sort_keys=True))
                f.write("\n")


# ------------------------------------------------------------------------- #
# Optional helpers for file scanning / injection
# ------------------------------------------------------------------------- #

def file_has_doc_id(path: Path) -> bool:
    """
    Best-effort check if a file already contains a doc_id in a canonical location.

    - For .py/.ps1: look for a header line starting with '# DOC_ID:' or '# doc_id:'.
    - For .md: look for 'doc_id:' in YAML frontmatter.
    - For others: simple heuristic search for 'doc_id:' in first ~50 lines.
    """
    if not path.is_file():
        return False

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False

    lines = text.splitlines()
    # Check top 50 lines only
    head = lines[:50]

    if path.suffix in {".py", ".ps1", ".psm1"}:
        for line in head:
            stripped = line.strip()
            if stripped.lower().startswith("# doc_id:") or stripped.lower().startswith("# DOC_ID:".lower()):
                return True
        return False

    if path.suffix in {".md", ".markdown"}:
        # Very simple YAML frontmatter detection
        if len(head) >= 3 and head[0].strip() == "---":
            for line in head[1:]:
                if line.strip() == "---":
                    break
                if line.strip().startswith("doc_id:"):
                    return True
        # Fallback search
        return any("doc_id:" in line for line in head)

    # Generic fallback
    return any("doc_id:" in line for line in head)


def inject_doc_id_into_file(path: Path, doc_id: str) -> None:
    """
    Insert a DOC_ID into the file at `path` if it's not already present.

    This is a conservative implementation:
    - For .py/.ps1: insert '# DOC_ID: ...' after any shebang and encoding lines.
    - For .md: insert/augment YAML frontmatter with 'doc_id: ...'.
    - For others: prepend a 'doc_id: ...' line at the top.
    """
    if not path.is_file():
        raise FileNotFoundError(path)

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise RuntimeError(f"Failed to read file for doc_id injection: {path}") from exc

    if file_has_doc_id(path):
        # Nothing to do
        return

    if path.suffix in {".py", ".ps1", ".psm1"}:
        lines = text.splitlines()
        insert_idx = 0

        # Skip shebang and encoding comments
        while insert_idx < len(lines):
            first = lines[insert_idx].strip()
            if first.startswith("#!") or "coding" in first.lower():
                insert_idx += 1
            else:
                break

        new_line = f"# DOC_ID: {doc_id}"
        lines.insert(insert_idx, new_line)
        new_text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
        path.write_text(new_text, encoding="utf-8")
        return

    if path.suffix in {".md", ".markdown"}:
        lines = text.splitlines()
        new_lines = []

        if lines and lines[0].strip() == "---":
            # Existing frontmatter: inject doc_id line if missing
            new_lines.append(lines[0])
            i = 1
            inserted = False

            # Process frontmatter block
            while i < len(lines):
                line = lines[i]
                if line.strip() == "---":
                    if not inserted:
                        new_lines.append(f"doc_id: {doc_id}")
                    new_lines.append(line)
                    i += 1
                    break
                if line.strip().startswith("doc_id:"):
                    # Replace existing value
                    new_lines.append(f"doc_id: {doc_id}")
                    inserted = True
                else:
                    new_lines.append(line)
                i += 1

            # Remainder of file
            new_lines.extend(lines[i:])
        else:
            # No frontmatter: add one
            new_lines = [
                "---",
                f"doc_id: {doc_id}",
                "---",
                "",
            ]
            new_lines.extend(lines)

        new_text = "\n".join(new_lines) + ("\n" if text.endswith("\n") else "")
        path.write_text(new_text, encoding="utf-8")
        return

    # Generic fallback: prepend a simple marker
    new_text = f"doc_id: {doc_id}\n{text}"
    path.write_text(new_text, encoding="utf-8")


# ------------------------------------------------------------------------- #
# Example mint_func implementation (placeholder)
# ------------------------------------------------------------------------- #

def example_mint_func(file_path: str, module_id: Optional[str] = None) -> str:
    """
    Very simple example mint_func for development/testing.

    You SHOULD replace this with a function that calls your real doc_id
    registry CLI or backend.

    Example output:
      DOC-core.state-001
      DOC-unknown-002
    """
    # Use a tiny local counter file under .state/ for testing
    state_dir = Path(".state")
    state_dir.mkdir(parents=True, exist_ok=True)
    counter_file = state_dir / "doc_id_counter.json"

    if counter_file.exists():
        data = json.loads(counter_file.read_text(encoding="utf-8"))
    else:
        data = {"next": 1}

    seq = data.get("next", 1)
    data["next"] = seq + 1
    counter_file.write_text(json.dumps(data), encoding="utf-8")

    # Derive a simple category from module_id or fallback
    if module_id:
        category = module_id.replace("mod.", "").replace(".", "_")
    else:
        category = "unknown"

    return f"DOC-{category}-{seq:03d}"
```

---

## 2. `WorktreeManager` Integration – Pseudo-Patch

Below is a **unified diff–style** pseudo-patch showing how to wire `IDCoordinator` into a typical `WorktreeManager`.

You’ll need to adapt function/attribute names (`_get_files_for_workstream`, `worktree_root`, etc.) to your actual code, but the integration pattern is clear.

```diff
--- a/orchestrator/worktrees.py
+++ b/orchestrator/worktrees.py
@@ -1,6 +1,11 @@
-from pathlib import Path
+from pathlib import Path
+from typing import List, Dict, Any, Optional
+
+from id_coordinator import (
+    IDCoordinator,
+    file_has_doc_id,
+    inject_doc_id_into_file,
+)

 
-class WorktreeManager:
+class WorktreeManager:
     """
     Manages creation of Git worktrees and execution of AI tools (e.g. aider)
     inside those worktrees for a given workstream.
@@ -9,13 +14,24 @@
     """
 
-    def __init__(self, repo_root: Path, ...):
+    def __init__(
+        self,
+        repo_root: Path,
+        id_coordinator: IDCoordinator,
+        *,
+        inventory_path: Path,
+        # ... any other existing parameters ...
+    ):
         self.repo_root = repo_root
+        self.id_coordinator = id_coordinator
+        self.inventory_path = inventory_path
         # existing init code...
 
 
@@
-    async def execute_in_worktree(self, ws_id: str, agent_id: str) -> None:
-        """
-        Create a worktree for the given workstream and run the AI tool inside it.
-        """
-        worktree_path = self._create_worktree(ws_id, agent_id)
+    async def execute_in_worktree(self, ws_spec: Dict[str, Any], agent_id: str) -> None:
+        """
+        Create a worktree for the given workstream and run the AI tool inside it.
+
+        ws_spec MUST contain:
+          - id: str
+          - files_to_edit: List[str]
+          - files_to_create: List[str]
+        """
+        ws_id = ws_spec["id"]
+        worktree_path = self._create_worktree(ws_id, agent_id)
+
+        # ------------------------------------------------------------------
+        # 1) Pre-assign doc_ids on MAIN for all files this workstream touches
+        # ------------------------------------------------------------------
+        files_to_edit: List[str] = ws_spec.get("files_to_edit", [])
+        files_to_create: List[str] = ws_spec.get("files_to_create", [])
+
+        self._ensure_doc_ids_on_main(files_to_edit, ws_spec)
+
+        # ------------------------------------------------------------------
+        # 2) Sync doc_ids into worktree copies BEFORE running AI tool
+        # ------------------------------------------------------------------
+        self._inject_doc_ids_into_worktree(worktree_path, files_to_edit, ws_spec)
+
+        # ------------------------------------------------------------------
+        # 3) Run AI tool inside worktree (unchanged, but now IDs are stable)
+        # ------------------------------------------------------------------
         try:
-            await self._run_aider(worktree_path, ws_id, agent_id)
+            await self._run_aider(worktree_path, ws_spec, agent_id)
         finally:
             # cleanup, logs, etc.
             self._cleanup_worktree(worktree_path)
@@
+    # ------------------------------------------------------------------+
+    # ID integration helpers
+    # ------------------------------------------------------------------+
+
+    def _ensure_doc_ids_on_main(self, files_to_edit: List[str], ws_spec: Dict[str, Any]) -> None:
+        """
+        Ensure that all existing files this workstream will edit have a doc_id
+        assigned in MAIN.
+
+        This:
+          - runs BEFORE creating the worktree
+          - uses IDCoordinator to mint doc_ids
+          - updates docs_inventory.jsonl via IDCoordinator
+
+        NOTE: this function does NOT patch the files on disk; you can choose
+        to patch on main here if desired, or only patch in worktrees.
+        """
+        for rel_path in files_to_edit:
+            main_path = (self.repo_root / rel_path).resolve()
+            if not main_path.exists():
+                # Could be a planned-new file incorrectly shown in files_to_edit
+                continue
+
+            # Optional: infer module_id from path and/or ws_spec
+            module_id = self._infer_module_id_for_path(rel_path, ws_spec)
+
+            # Ask IDCoordinator for a doc_id (mint if needed)
+            self.id_coordinator.assign_doc_id(rel_path, module_id=module_id)
+
+            # Optionally, you could choose to inject doc_id on MAIN here:
+            # if not file_has_doc_id(main_path):
+            #     inject_doc_id_into_file(main_path, self.id_coordinator.assign_doc_id(rel_path, module_id))
+
+
+    def _inject_doc_ids_into_worktree(
+        self,
+        worktree_path: Path,
+        files_to_edit: List[str],
+        ws_spec: Dict[str, Any],
+    ) -> None:
+        """
+        Ensure the worktree copies of files_to_edit have doc_ids injected
+        before the AI tool runs.
+
+        This is where we actually modify files inside the worktree.
+        """
+        for rel_path in files_to_edit:
+            main_rel = rel_path
+
+            # Determine doc_id via coordinator (no new minting if already assigned)
+            module_id = self._infer_module_id_for_path(main_rel, ws_spec)
+            doc_id = self.id_coordinator.assign_doc_id(main_rel, module_id=module_id)
+
+            wt_file = (worktree_path / rel_path).resolve()
+            if not wt_file.exists():
+                # Might be removed/renamed in this workstream; skip
+                continue
+
+            # Inject doc_id into worktree file if missing
+            if not file_has_doc_id(wt_file):
+                inject_doc_id_into_file(wt_file, doc_id)
+
+
+    def _infer_module_id_for_path(self, rel_path: str, ws_spec: Dict[str, Any]) -> Optional[str]:
+        """
+        Best-effort inference of module_id from path or workstream metadata.
+
+        This is intentionally simple and project-specific; customize as needed.
+        """
+        # Example: map 'modules/core/state/...' -> 'mod.core.state'
+        parts = Path(rel_path).parts
+        if len(parts) >= 3 and parts[0] == "modules":
+            # modules/<layer>/<name>/...
+            layer = parts[1]
+            name = parts[2]
+            return f"mod.{layer}.{name}".replace("-", "_")
+
+        # Fallback: read from ws_spec if provided
+        return ws_spec.get("default_module_id")
```

---

### How to use this

**1. Wire up `IDCoordinator` in your orchestrator bootstrap**

```python
# bootstrap_orchestrator.py
from pathlib import Path
from id_coordinator import IDCoordinator, example_mint_func
from orchestrator.worktrees import WorktreeManager

repo_root = Path(".").resolve()
inventory_path = repo_root / ".state" / "docs_inventory.jsonl"

id_coord = IDCoordinator(
    inventory_path=inventory_path,
    mint_func=example_mint_func,  # replace with your real mint function
)

worktrees = WorktreeManager(
    repo_root=repo_root,
    id_coordinator=id_coord,
    inventory_path=inventory_path,
    # ... other args ...
)
```

**2. Ensure workstream specs include `files_to_edit` / `files_to_create`**

Once those are present, you can start letting the orchestrator:

* pre-assign `doc_id`s via `IDCoordinator`,
* inject them into worktrees,
* keep `docs_inventory.jsonl` up to date incrementally.

If you paste your actual `WorktreeManager` and/or registry CLI interface later, I can tighten this patch into a near drop-in diff for your repo.
