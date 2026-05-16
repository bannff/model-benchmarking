from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Union

from ..models import Sample
from .errors import DatasetError
from .validation import _matches_taxonomy_filter

def load_dataset(
    path: Union[str, Path],
    *,
    max_samples: Optional[int] = None,
    sample_tags: Optional[List[str]] = None,
    taxonomy_filter: Optional[Dict[str, Union[str, List[str]]]] = None,
    base_dir: Optional[Path] = None,
) -> Iterator[Sample]:
    """
    Load samples from a JSONL dataset file.
    """
    dataset_path = Path(path)
    if not dataset_path.is_absolute() and base_dir:
        dataset_path = base_dir / dataset_path
    
    if not dataset_path.exists():
        raise DatasetError(f"Dataset file not found: {dataset_path}")
    
    if not dataset_path.suffix.lower() in (".jsonl", ".json"):
        raise DatasetError(f"Dataset must be .jsonl or .json: {dataset_path}")
    
    count = 0
    auto_id = 0
    
    try:
        with open(dataset_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    raise DatasetError(f"Invalid JSON on line {line_num} of {dataset_path}: {e}")
                
                if "input" not in data:
                    raise DatasetError(f"Missing 'input' field on line {line_num} of {dataset_path}")
                
                if "id" not in data:
                    data["id"] = auto_id
                    auto_id += 1
                
                try:
                    sample = Sample.model_validate(data)
                except Exception as e:
                    raise DatasetError(f"Invalid sample on line {line_num} of {dataset_path}: {e}")
                
                if sample_tags:
                    if not any(tag in sample.tags for tag in sample_tags):
                        continue
                
                if taxonomy_filter and not _matches_taxonomy_filter(sample, taxonomy_filter):
                    continue
                
                yield sample
                count += 1
                
                if max_samples is not None and count >= max_samples:
                    return
                    
    except IOError as e:
        raise DatasetError(f"Error reading dataset file {dataset_path}: {e}")


def load_dataset_list(
    path: Union[str, Path],
    *,
    max_samples: Optional[int] = None,
    sample_tags: Optional[List[str]] = None,
    taxonomy_filter: Optional[Dict[str, Union[str, List[str]]]] = None,
    base_dir: Optional[Path] = None,
) -> List[Sample]:
    """Load all samples from a dataset into a list."""
    return list(load_dataset(
        path,
        max_samples=max_samples,
        sample_tags=sample_tags,
        taxonomy_filter=taxonomy_filter,
        base_dir=base_dir,
    ))


def count_samples(
    path: Union[str, Path],
    base_dir: Optional[Path] = None,
) -> int:
    """Count the number of valid samples in a dataset without loading them all."""
    count = 0
    for _ in load_dataset(path, base_dir=base_dir):
        count += 1
    return count
