"""
Utility for saving evaluation results and generating reports.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


def save_suite_results(
    suite_name: str,
    output_dir: str,
    results: Dict[str, Any],
    filename: Optional[str] = None
) -> str:
    """
    Save suite results to a JSON file.
    
    Args:
        suite_name: Name of the suite (used for default filename).
        output_dir: Directory to save in.
        results: The results dictionary.
        filename: Optional specific filename.
        
    Returns:
        The absolute path to the saved file.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    if not filename:
        filename = f"{suite_name}_results.json"
        
    file_path = out_path / filename
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
        
    return str(file_path.resolve())
