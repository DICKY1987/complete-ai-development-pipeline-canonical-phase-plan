from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

try:
    import yaml  # type: ignore
except Exception as exc:  # noqa: BLE001
    yaml = None  # type: ignore
    _YAML_IMPORT_ERROR = exc
else:
    _YAML_IMPORT_ERROR = None


class PathRegistryError(Exception):
    """Raised when a path registry lookup or validation fails."""


_DEFAULT_REGISTRY_PATHS: Tuple[Path, ...] = (
    Path("config/path_index.yaml"),
    Path("phase0_bootstrap/config/path_index.yaml"),
)

_env_path = os.environ.get("PATH_REGISTRY_FILE")
_registry_candidates = []
if _env_path:
    _registry_candidates.append(Path(_env_path))
for p in _DEFAULT_REGISTRY_PATHS:
    if p not in _registry_candidates:
        _registry_candidates.append(p)
_REGISTRY_PATHS: Tuple[Path, ...] = tuple(_registry_candidates)

_ACTIVE_REGISTRY_PATH: Path | None = None
_RAW_CACHE: Dict[str, Any] | None = None
_FLAT_CACHE: Dict[str, Dict[str, Any]] | None = None


def clear_cache() -> None:
    """Clear all in-memory caches and active registry pointer."""
    global _RAW_CACHE, _FLAT_CACHE, _ACTIVE_REGISTRY_PATH
    _RAW_CACHE = None
    _FLAT_CACHE = None
    _ACTIVE_REGISTRY_PATH = None


def _require_yaml() -> None:
    if yaml is None:  # type: ignore
        raise ImportError(
            "PyYAML is required to use the path registry"
        ) from _YAML_IMPORT_ERROR


def _select_registry_path() -> Path:
    for candidate in _REGISTRY_PATHS:
        c_path = Path(candidate)
        if c_path.exists():
            return c_path
    raise FileNotFoundError(
        f"No path registry file found. Checked: {', '.join(str(p) for p in _REGISTRY_PATHS)}"
    )


def _load_registry_raw() -> Dict[str, Any]:
    """Load the registry YAML as a dictionary."""
    global _RAW_CACHE, _ACTIVE_REGISTRY_PATH
    if _RAW_CACHE is not None and _ACTIVE_REGISTRY_PATH is not None:
        return _RAW_CACHE

    _require_yaml()
    registry_path = _select_registry_path()
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))  # type: ignore
    if not isinstance(data, dict) or "paths" not in data:
        raise ValueError("Path registry must contain a top-level 'paths' mapping")

    _RAW_CACHE = data  # type: ignore[assignment]
    _ACTIVE_REGISTRY_PATH = registry_path
    return data  # type: ignore[return-value]


def _normalize_path(value: str) -> str:
    return str(Path(value))


def _flatten_paths(tree: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    paths = tree.get("paths")
    if not isinstance(paths, dict):
        raise ValueError("Expected a 'paths' mapping in the registry")

    flat: Dict[str, Dict[str, Any]] = {}
    for namespace, entries in paths.items():
        if not isinstance(entries, dict):
            raise ValueError(f"Invalid entries for namespace '{namespace}'")
        for name, meta in entries.items():
            if not isinstance(meta, dict):
                raise ValueError(f"Invalid metadata for key '{namespace}.{name}'")
            key = f"{namespace}.{name}"
            flat[key] = {**meta}
            if "path" in flat[key] and flat[key]["path"] is not None:
                flat[key]["path"] = _normalize_path(str(flat[key]["path"]))
    return flat


def _load_flat_registry() -> Dict[str, Dict[str, Any]]:
    global _FLAT_CACHE
    if _FLAT_CACHE is not None:
        return _FLAT_CACHE

    raw = _load_registry_raw()
    _FLAT_CACHE = _flatten_paths(raw)
    return _FLAT_CACHE


def list_paths(section: str | None = None) -> Dict[str, str]:
    """Return mapping of key -> path, optionally filtered by section."""
    flat = _load_flat_registry()
    result_items: Iterable[tuple[str, str]]
    filtered = []
    for key, meta in flat.items():
        if section is not None and meta.get("section") != section:
            continue
        path_value = meta.get("path")
        if not path_value:
            continue
        filtered.append((key, _normalize_path(str(path_value))))

    result_items = filtered
    return dict(result_items)


def resolve_path(key: str) -> str:
    """Resolve a path key to a repo-relative path string."""
    if not key or "." not in key:
        raise PathRegistryError(
            "Path key must be non-empty and namespaced (e.g. ns.name)"
        )

    flat = _load_flat_registry()
    meta = flat.get(key)
    if meta is None:
        raise PathRegistryError(f"Unknown path key: {key}")

    path_value = meta.get("path")
    if not path_value:
        raise PathRegistryError(f"Path value missing for key: {key}")

    return _normalize_path(str(path_value))


def registry_path() -> Path:
    """Return the currently loaded registry path (forces selection if not loaded)."""
    if _ACTIVE_REGISTRY_PATH is not None:
        return _ACTIVE_REGISTRY_PATH
    return _select_registry_path()


__all__ = [
    "PathRegistryError",
    "clear_cache",
    "list_paths",
    "resolve_path",
    "_flatten_paths",
    "_load_registry_raw",
    "_REGISTRY_PATHS",
    "registry_path",
]
