"""
Run metadata helpers: generate run_id, capture environment, git commit, etc.
"""
from __future__ import annotations

import hashlib
import os
import platform
import subprocess
from datetime import datetime
from typing import Dict, Any


def new_run_id(prefix: str | None = None) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    rand = hashlib.sha1(os.urandom(16)).hexdigest()[:6]
    base = f"{ts}-{rand}"
    return f"{prefix}-{base}" if prefix else base


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, timeout=2)
        return out.decode().strip()
    except Exception:
        return None


def collect_environment_snapshot() -> Dict[str, Any]:
    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "git_commit": _git_commit(),
    }
