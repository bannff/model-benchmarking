from __future__ import annotations

import os
import re
from typing import Any

def interpolate_env_vars(value: str) -> str:
    """
    Interpolate environment variables in a string.
    
    Supports:
    - ${VAR} - replaced with VAR value or empty string
    - ${VAR:-default} - replaced with VAR value or "default"
    """
    def replacer(match: re.Match[str]) -> str:
        var = match.group(1)
        default = match.group(3) if match.group(3) else ""
        return os.environ.get(var, default)
    
    # Pattern: ${VAR} or ${VAR:-default}
    pattern = r"\$\{([A-Za-z_][A-Za-z0-9_]*)(:-([^}]*))?\}"
    return re.sub(pattern, replacer, value)


def process_values(obj: Any) -> Any:
    """Recursively process values, interpolating env vars in strings."""
    if isinstance(obj, str):
        return interpolate_env_vars(obj)
    elif isinstance(obj, dict):
        return {k: process_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [process_values(item) for item in obj]
    return obj
