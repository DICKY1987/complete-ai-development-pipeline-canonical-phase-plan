"""Ensure repository root modules are discoverable during UETF tests."""
import sys
from pathlib import Path


_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.append(str(_repo_root))

# Ensure system site-packages are on path for optional deps (e.g., jsonschema)
try:
    import site

    for p in site.getsitepackages() + [site.getusersitepackages()]:
        if p and p not in sys.path:
            sys.path.append(p)
except Exception:
    pass
