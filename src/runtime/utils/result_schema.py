"""
Standard result envelope and helpers for writing manifests and index.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict
from datetime import datetime, timezone
import json
from pathlib import Path


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
    return datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"


def write_manifest(envelope: ResultEnvelope, output_dir: str) -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    path = output_path / f"manifest_{envelope.run_id}.json"
    path.write_text(json.dumps(envelope.to_dict(), indent=2), encoding="utf-8")
    return str(path)


def append_index(envelope: ResultEnvelope, output_dir: str) -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    idx = output_path / "index.jsonl"
    with idx.open("a", encoding="utf-8") as f:
        f.write(json.dumps(envelope.to_dict()) + "\n")
    return str(idx)
