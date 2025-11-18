from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "PyYAML is required for path registry. Install with: pip install PyYAML"
    ) from exc


_CACHE: Dict[str, Any] | None = None
_REGISTRY_PATHS = (
    Path("config") / "path_index.yaml",
    Path("config") / "paths.yaml",
)


class PathRegistryError(KeyError):
    pass


def _load_registry_raw() -> Dict[str, Any]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    cfg_path: Optional[Path] = None
    for p in _REGISTRY_PATHS:
        if p.exists():
            cfg_path = p
            break

    if cfg_path is None:
        raise FileNotFoundError(
            "Path registry not found. Expected one of: "
            + ", ".join(str(p) for p in _REGISTRY_PATHS)
        )

    with cfg_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    if not isinstance(data, dict) or "paths" not in data:
        raise ValueError(
            f"Malformed path registry at {cfg_path}. Expected top-level 'paths' mapping."
        )

    _CACHE = data
    return _CACHE


def _flatten_paths(tree: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}
    paths = tree.get("paths", {})
    if not isinstance(paths, dict):
        return result
    for namespace, entries in paths.items():
        if not isinstance(entries, dict):
            continue
        for key, meta in entries.items():
            if not isinstance(meta, dict):
                continue
            dotted = f"{namespace}.{key}"
            result[dotted] = meta
    return result


def list_paths(section: str | None = None) -> Dict[str, str]:
    tree = _load_registry_raw()
    flat = _flatten_paths(tree)
    out: Dict[str, str] = {}
    for k, meta in flat.items():
        if section is not None and meta.get("section") != section:
            continue
        path = meta.get("path")
        if isinstance(path, str):
            out[k] = path
    return out


def resolve_path(key: str) -> str:
    """
    Resolve a dotted key (e.g. 'phase_docs.ph02_state_layer_spec') to a repo-relative path.
    Raises PathRegistryError on unknown key or missing path value.
    """
    if not key or "." not in key:
        raise PathRegistryError(
            f"Invalid key '{key}'. Expected a dotted name like 'namespace.item'."
        )

    tree = _load_registry_raw()
    flat = _flatten_paths(tree)
    meta = flat.get(key)
    if meta is None:
        raise PathRegistryError(f"Unknown path key: {key}")
    path = meta.get("path")
    if not isinstance(path, str) or not path:
        raise PathRegistryError(f"Path missing for key: {key}")
    # Normalize to OS-specific separators but keep repo-relative behavior
    return str(Path(path))


def clear_cache() -> None:
    global _CACHE
    _CACHE = None

