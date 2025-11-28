from __future__ import annotations

import threading
from pathlib import Path
from typing import Dict, Tuple

import yaml

# Registry locations can be overridden for testing (see tests/test_path_registry.py)
_REGISTRY_PATHS: Tuple[Path, ...] = (Path("config/path_index.yaml"),)
_CACHE_LOCK = threading.Lock()
_CACHE: Dict[str, Dict[str, str]] | None = None


class PathRegistryError(Exception):
    """Raised for invalid keys or malformed registry entries."""


def clear_cache() -> None:
    """Reset the in-memory cache (used by tests and callers performing updates)."""
    global _CACHE
    with _CACHE_LOCK:
        _CACHE = None


def _load_registry_raw() -> dict:
    """Load and return the raw registry structure from YAML."""
    last_exc: Exception | None = None
    for candidate in _REGISTRY_PATHS:
        if not candidate.exists():
            last_exc = FileNotFoundError(candidate)
            continue
        data = yaml.safe_load(candidate.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "paths" not in data:
            raise ValueError("Registry must contain top-level 'paths' mapping")
        return data["paths"]
    if last_exc:
        raise last_exc
    raise FileNotFoundError("No registry file found")


def _flatten_paths(tree: dict) -> Dict[str, Dict[str, str]]:
    """Flatten the nested namespace/items into dotted-key metadata."""
    flat: Dict[str, Dict[str, str]] = {}
    for namespace, items in tree.items():
        if not isinstance(items, dict):
            continue
        for item, meta in items.items():
            key = f"{namespace}.{item}"
            if not isinstance(meta, dict):
                continue
            flat[key] = meta
    return flat


def _load_flattened() -> Dict[str, Dict[str, str]]:
    global _CACHE
    with _CACHE_LOCK:
        if _CACHE is not None:
            return _CACHE
        tree = _load_registry_raw()
        _CACHE = _flatten_paths(tree)
        return _CACHE


def resolve_path(key: str) -> str:
    """Resolve a dotted key to a repo-relative path string."""
    if not key or "." not in key:
        raise PathRegistryError(f"Invalid key: {key!r}")
    flat = _load_flattened()
    meta = flat.get(key)
    if meta is None:
        raise PathRegistryError(f"Unknown path key: {key}")
    path_value = meta.get("path")
    if not path_value:
        raise PathRegistryError(f"Missing path for key: {key}")
    return str(Path(path_value))


def list_paths(section: str | None = None) -> Dict[str, str]:
    """Return mapping of key->path; optionally filter by section."""
    flat = _load_flattened()
    result: Dict[str, str] = {}
    for key, meta in flat.items():
        if section is not None and meta.get("section") != section:
            continue
        path_value = meta.get("path")
        if path_value:
            result[key] = str(Path(path_value))
    return result
