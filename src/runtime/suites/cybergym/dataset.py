"""
Task loading for CyberGym.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def load_cybergym_tasks(sample_file: Path) -> List[Dict[str, Any]]:
    """Load tasks from a JSON or JSONL file."""
    tasks: List[Dict[str, Any]] = []
    if not sample_file.exists():
        raise FileNotFoundError(f"CyberGym sample file not found: {sample_file}")

    with sample_file.open("r", encoding="utf-8") as f:
        # Try JSONL first
        try:
            for line in f:
                if stripped := line.strip():
                    tasks.append(json.loads(stripped))
            if tasks:
                return tasks
        except json.JSONDecodeError:
            pass
            
        # Fallback to JSON array
        f.seek(0)
        data = json.load(f)
        if isinstance(data, list):
            return data
            
    return tasks
