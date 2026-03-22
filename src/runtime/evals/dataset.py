"""
Dataset loading utilities.

Supports JSONL files with the following format:
    {"input": "...", "ground_truth": "...", "metadata": {...}, "tags": [...]}

Each line is parsed into a Sample object.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Union

from .models import Sample


class DatasetError(Exception):
    """Error loading or parsing a dataset."""
    pass


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
    
    Args:
        path: Path to the JSONL file
        max_samples: Maximum number of samples to return
        sample_tags: Only return samples with at least one of these tags
        taxonomy_filter: Only return samples matching taxonomy criteria
                         Format: {"dimension": "value"} or {"dimension": ["val1", "val2"]}
                         Uses OR within dimension, AND across dimensions
        base_dir: Base directory for resolving relative paths
    
    Yields:
        Sample objects
    
    Raises:
        DatasetError: If the file cannot be read or parsed
    """
    # Resolve path
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
                    raise DatasetError(
                        f"Invalid JSON on line {line_num} of {dataset_path}: {e}"
                    )
                
                # Validate required fields
                if "input" not in data:
                    raise DatasetError(
                        f"Missing 'input' field on line {line_num} of {dataset_path}"
                    )
                
                # Auto-assign ID if not present
                if "id" not in data:
                    data["id"] = auto_id
                    auto_id += 1
                
                # Parse into Sample
                try:
                    sample = Sample.model_validate(data)
                except Exception as e:
                    raise DatasetError(
                        f"Invalid sample on line {line_num} of {dataset_path}: {e}"
                    )
                
                # Filter by tags if specified
                if sample_tags:
                    if not any(tag in sample.tags for tag in sample_tags):
                        continue
                
                # Filter by taxonomy if specified
                if taxonomy_filter and not _matches_taxonomy_filter(sample, taxonomy_filter):
                    continue
                
                yield sample
                count += 1
                
                # Check max samples limit
                if max_samples is not None and count >= max_samples:
                    return
                    
    except IOError as e:
        raise DatasetError(f"Error reading dataset file {dataset_path}: {e}")


def _matches_taxonomy_filter(
    sample: Sample,
    filters: Dict[str, Union[str, List[str]]],
) -> bool:
    """
    Check if a sample matches taxonomy filters.
    
    Uses OR within a dimension (any value matches), AND across dimensions.
    """
    if sample.taxonomy is None:
        return False
    
    for dim, required_values in filters.items():
        if dim not in sample.taxonomy:
            return False
        
        sample_values = sample.get_taxonomy_values(dim)
        required_list = [required_values] if isinstance(required_values, str) else required_values
        
        # OR within dimension: at least one required value must be present
        if not any(rv in sample_values for rv in required_list):
            return False
    
    return True


def load_dataset_list(
    path: Union[str, Path],
    *,
    max_samples: Optional[int] = None,
    sample_tags: Optional[List[str]] = None,
    taxonomy_filter: Optional[Dict[str, Union[str, List[str]]]] = None,
    base_dir: Optional[Path] = None,
) -> List[Sample]:
    """
    Load all samples from a dataset into a list.
    
    This is a convenience wrapper around load_dataset() for cases
    where you need random access to samples.
    """
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


def validate_dataset(
    path: Union[str, Path],
    base_dir: Optional[Path] = None,
) -> List[str]:
    """
    Validate a dataset file and return a list of errors.
    
    Returns:
        List of error messages (empty if valid)
    """
    errors: List[str] = []
    dataset_path = Path(path)
    
    if not dataset_path.is_absolute() and base_dir:
        dataset_path = base_dir / dataset_path
    
    if not dataset_path.exists():
        return [f"Dataset file not found: {dataset_path}"]
    
    try:
        with open(dataset_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    errors.append(f"Line {line_num}: Invalid JSON - {e}")
                    continue
                
                if "input" not in data:
                    errors.append(f"Line {line_num}: Missing 'input' field")
                
                # Validate as Sample
                try:
                    Sample.model_validate(data)
                except Exception as e:
                    errors.append(f"Line {line_num}: Validation error - {e}")
                    
    except IOError as e:
        errors.append(f"Error reading file: {e}")
    
    return errors
