from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

from ..models import SuiteSpec
from .errors import SuiteLoadError
from .interpolation import process_values

class SuiteLoader:
    """
    Loads suite configurations from YAML or JSON files.
    """
    
    @classmethod
    def load(
        cls,
        path: Union[str, Path],
        overrides: Optional[Dict[str, Any]] = None,
    ) -> SuiteSpec:
        """Load a suite configuration from a file."""
        config_path = Path(path)
        
        if not config_path.exists():
            raise SuiteLoadError(f"Suite config not found: {config_path}")
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                if config_path.suffix in (".yaml", ".yml"):
                    data = yaml.safe_load(f)
                else:
                    import json
                    data = json.load(f)
        except Exception as e:
            raise SuiteLoadError(f"Failed to parse {config_path}: {e}")
        
        if not isinstance(data, dict):
            raise SuiteLoadError(f"Suite config must be a dict, got {type(data)}")
        
        # Process environment variable interpolation
        data = process_values(data)
        
        # Apply overrides
        if overrides:
            data = cls._deep_merge(data, overrides)
        
        # Set base_dir for relative path resolution
        data["base_dir"] = config_path.parent
        
        # Validate and create SuiteSpec
        try:
            return SuiteSpec.model_validate(data)
        except Exception as e:
            raise SuiteLoadError(f"Invalid suite configuration: {e}")
    
    @staticmethod
    def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dicts, with override taking precedence."""
        result = base.copy()
        
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = SuiteLoader._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @classmethod
    def validate(cls, path: Union[str, Path]) -> list[str]:
        """Validate a suite configuration without fully loading it."""
        errors: list[str] = []
        config_path = Path(path)
        
        if not config_path.exists():
            return [f"File not found: {config_path}"]
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                if config_path.suffix in (".yaml", ".yml"):
                    data = yaml.safe_load(f)
                else:
                    import json
                    data = json.load(f)
        except Exception as e:
            return [f"Parse error: {e}"]
        
        if not isinstance(data, dict):
            return [f"Config must be a dict, got {type(data).__name__}"]
        
        required = ["name", "dataset", "graders", "gate"]
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if "dataset" in data:
            dataset_path = Path(data["dataset"])
            if not dataset_path.is_absolute():
                dataset_path = config_path.parent / dataset_path
            if not dataset_path.exists():
                errors.append(f"Dataset not found: {dataset_path}")
        
        if not errors:
            try:
                data["base_dir"] = config_path.parent
                SuiteSpec.model_validate(data)
            except Exception as e:
                errors.append(f"Validation error: {e}")
        
        return errors
