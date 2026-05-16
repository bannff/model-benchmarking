from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..models import Sample

def _matches_taxonomy_filter(
    sample: Sample,
    filters: Dict[str, Union[str, List[str]]],
) -> bool:
    """
    Check if a sample matches taxonomy filters.
    """
    if sample.taxonomy is None:
        return False
    
    for dim, required_values in filters.items():
        if dim not in sample.taxonomy:
            return False
        
        sample_values = sample.get_taxonomy_values(dim)
        required_list = [required_values] if isinstance(required_values, str) else required_values
        
        if not any(rv in sample_values for rv in required_list):
            return False
    
    return True


def validate_dataset(
    path: Union[str, Path],
    base_dir: Optional[Path] = None,
) -> List[str]:
    """
    Validate a dataset file and return a list of errors.
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
                
                try:
                    Sample.model_validate(data)
                except Exception as e:
                    errors.append(f"Line {line_num}: Validation error - {e}")
                    
    except IOError as e:
        errors.append(f"Error reading file: {e}")
    
    return errors
