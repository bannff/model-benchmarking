"""
Dataset loading utilities for CS-Eval.
Handles both Hugging Face and local JSON/JSONL formats.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class LocalDataset:
    """Mock-like interface for locally loaded datasets to match HF Dataset API."""
    def __init__(self, items: List[Dict[str, Any]]):
        self._items = items
        self.features = {k: True for k in (items[0].keys() if items else [])}

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        return self._items[idx]


def load_cs_eval_dataset(
    split: str = "test", 
    local_path: Optional[str] = None,
    verbose: bool = False
) -> Any:
    """
    Load the CS-Eval dataset.
    
    Args:
        split: HF dataset split.
        local_path: Optional path to local JSON/JSONL sample.
        verbose: Enable verbose logging.
    """
    if local_path:
        return _load_local_dataset(local_path, verbose)
    
    return _load_hf_dataset(split, verbose)


def _load_local_dataset(path: str, verbose: bool) -> LocalDataset:
    """Load dataset from a local JSON or JSONL file."""
    if verbose:
        print(f"📄 Loading local CS-Eval sample: {path}")
    
    items: List[Dict[str, Any]] = []
    p = Path(path)
    
    if p.suffix.lower() in (".jsonl", ".txt"):
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if stripped := line.strip():
                    items.append(json.loads(stripped))
    else:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Local sample JSON must be a list of items")
            items = data
            
    dataset = LocalDataset(items)
    if verbose:
        print(f"✅ Loaded {len(dataset)} questions from local sample")
    return dataset


def _load_hf_dataset(split: str, verbose: bool) -> Any:
    """Load dataset from Hugging Face."""
    try:
        from datasets import load_dataset
        dataset = load_dataset("cseval/cs-eval", split=split)
        if verbose:
            print(f"✅ Loaded {len(dataset)} questions from CS-Eval HF")
        return dataset
    except ImportError:
        raise RuntimeError("'datasets' package not installed; use local sample or install datasets")
    except Exception as e:
        raise RuntimeError(f"Error loading CS-Eval from HF: {e}")
