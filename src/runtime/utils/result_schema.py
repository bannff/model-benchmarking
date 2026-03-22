"""
Standard result envelope and helpers for writing manifests and index.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict
from datetime import datetime
import json
import os


@dataclass
class ResultEnvelope:
    run_id: str
    suite: str
    model: str
    provider: str
    started_at: str
    finished_at: str
    status: str
    metrics: Dict[str, Any]
    artifacts: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def iso_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def write_manifest(envelope: ResultEnvelope, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"manifest_{envelope.run_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(envelope.to_dict(), f, indent=2)
    return path


def append_index(envelope: ResultEnvelope, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    idx = os.path.join(output_dir, "index.jsonl")
    with open(idx, "a", encoding="utf-8") as f:
        f.write(json.dumps(envelope.to_dict()) + "\n")
    return idx
