"""
Core runner for CVE-Bench evaluations.
"""
from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime.providers.base import BaseProvider


async def run_cve_bench(
    provider: BaseProvider,
    output_dir: str,
    cvebench_config: Optional[Dict[str, Any]] = None,
    verbose: bool = False
) -> Dict[str, Any]:
    """Run the CVE-Bench benchmark."""
    start_time = time.time()
    
    cfg = cvebench_config or {}
    repo_root = Path(__file__).resolve().parents[3]
    run_script = Path(__file__).parent / "scripts" / "run"
    
    status = "ok"
    message = ""
    
    if run_script.exists():
        try:
            cmd = ["bash", str(run_script), "eval"]
            if cfg.get("model"):
                cmd.append(f"--model={cfg['model']}")
            
            targets = cfg.get("targets") or []
            if isinstance(targets, list):
                for target in targets:
                    cmd.extend(["-T", str(target)])
                    
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            message = (proc.stdout or proc.stderr or "").strip()
            status = "ok" if proc.returncode == 0 else f"exit {proc.returncode}"
        except Exception as e:
            status = f"error: {e}"
            message = str(e)
    else:
        status = "skipped (run script not found)"
        message = f"Looked in: {run_script}"

    duration = time.time() - start_time
    metrics = {
        "invocation_status": status,
        "duration_seconds": duration
    }
    
    return {
        "suite": "cve_bench",
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": duration,
        "metrics": metrics,
        "message": message
    }
