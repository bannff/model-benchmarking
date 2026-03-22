"""
Suite configuration loader.

Loads and validates YAML/JSON suite configuration files.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

from .models import SuiteSpec, TargetSpec, GateSpec


class SuiteLoadError(Exception):
    """Error loading a suite configuration."""
    pass


class SuiteLoader:
    """
    Loads suite configurations from YAML or JSON files.
    
    Supports:
    - Environment variable interpolation (${VAR} or ${VAR:-default})
    - Relative path resolution
    - Validation via Pydantic models
    """
    
    @staticmethod
    def _interpolate_env_vars(value: str) -> str:
        """
        Interpolate environment variables in a string.
        
        Supports:
        - ${VAR} - replaced with VAR value or empty string
        - ${VAR:-default} - replaced with VAR value or "default"
        """
        def replacer(match: re.Match[str]) -> str:
            var = match.group(1)
            default = match.group(3) if match.group(3) else ""
            return os.environ.get(var, default)
        
        # Pattern: ${VAR} or ${VAR:-default}
        pattern = r"\$\{([A-Za-z_][A-Za-z0-9_]*)(:-([^}]*))?\}"
        return re.sub(pattern, replacer, value)
    
    @classmethod
    def _process_values(cls, obj: Any) -> Any:
        """Recursively process values, interpolating env vars in strings."""
        if isinstance(obj, str):
            return cls._interpolate_env_vars(obj)
        elif isinstance(obj, dict):
            return {k: cls._process_values(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [cls._process_values(item) for item in obj]
        return obj
    
    @classmethod
    def load(
        cls,
        path: Union[str, Path],
        overrides: Optional[Dict[str, Any]] = None,
    ) -> SuiteSpec:
        """
        Load a suite configuration from a file.
        
        Args:
            path: Path to YAML or JSON config file
            overrides: Optional dict of overrides to merge
        
        Returns:
            Validated SuiteSpec
        
        Raises:
            SuiteLoadError: If file cannot be loaded or validated
        """
        config_path = Path(path)
        
        if not config_path.exists():
            raise SuiteLoadError(f"Suite config not found: {config_path}")
        
        # Load the file
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
        data = cls._process_values(data)
        
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
        """
        Validate a suite configuration without fully loading it.
        
        Args:
            path: Path to config file
        
        Returns:
            List of validation errors (empty if valid)
        """
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
        
        # Check required fields
        required = ["name", "dataset", "graders", "gate"]
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check dataset exists
        if "dataset" in data:
            dataset_path = Path(data["dataset"])
            if not dataset_path.is_absolute():
                dataset_path = config_path.parent / dataset_path
            if not dataset_path.exists():
                errors.append(f"Dataset not found: {dataset_path}")
        
        # Try to validate with Pydantic
        if not errors:
            try:
                data["base_dir"] = config_path.parent
                SuiteSpec.model_validate(data)
            except Exception as e:
                errors.append(f"Validation error: {e}")
        
        return errors


def load_suite(
    path: Union[str, Path],
    overrides: Optional[Dict[str, Any]] = None,
) -> SuiteSpec:
    """
    Convenience function to load a suite configuration.
    
    Args:
        path: Path to YAML or JSON config file
        overrides: Optional dict of overrides to merge
    
    Returns:
        Validated SuiteSpec
    """
    return SuiteLoader.load(path, overrides)
