"""
Lightweight config loading and deep-merge utilities.

Supports YAML and JSON. TOML is supported if tomllib (3.11+) or tomli is available.
No hard dependency on TOML is introduced.
"""
from __future__ import annotations

from typing import Any, Dict
import json
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore

try:  # Python 3.11+
    import tomllib as toml_loader  # type: ignore
except Exception:  # pragma: no cover
    try:
        import tomli as toml_loader  # type: ignore
    except Exception:  # pragma: no cover
        toml_loader = None  # type: ignore


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep-merge two dicts with override taking precedence.

    Lists and scalars are replaced, nested dicts are merged recursively.
    """
    out = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)  # type: ignore[arg-type]
        else:
            out[k] = v
    return out


def load_config_file(path: str | Path | None) -> Dict[str, Any]:
    if not path:
        return {}
    
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(str(config_path))
    
    ext = config_path.suffix.lower()
    with open(config_path, "rb") as f:
        data: Dict[str, Any]
        if ext in (".yml", ".yaml"):
            if yaml is None:
                raise RuntimeError("PyYAML not installed but YAML config provided")
            data = yaml.safe_load(f) or {}
        elif ext == ".json":
            data = json.load(f) or {}
        elif ext == ".toml":
            if toml_loader is None:
                raise RuntimeError("tomllib/tomli not available for TOML config")
            loaded = toml_loader.load(f)  # type: ignore[operator]
            data = dict(loaded or {})  # type: ignore[arg-type]
        else:
            raise ValueError(f"Unsupported config extension: {ext}")
    # Guarantee mapping type for callers
    return dict(data)
