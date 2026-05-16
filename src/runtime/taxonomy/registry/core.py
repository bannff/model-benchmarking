"""
Taxonomy registry for loading, storing, and accessing taxonomies.

Provides:
- Built-in cybersecurity taxonomy
- Loading from YAML files
- Global registry for taxonomy access
"""
from __future__ import annotations

from pathlib import Path
from .defaults.cyber_taxonomy import get_cybersecurity_taxonomy
from typing import Any, Dict, List, Optional, Union
import yaml

from ..schema import (
    TaxonomySpec,
    TaxonomyDimension,
    TaxonomyNode,
)


class TaxonomyRegistry:
    """
    Global registry for taxonomy specifications.
    
    Manages loading, caching, and access to taxonomy definitions.
    """
    
    _instance: Optional["TaxonomyRegistry"] = None
    _taxonomies: Dict[str, TaxonomySpec]
    
    def __new__(cls) -> "TaxonomyRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._taxonomies = {}
            cls._instance._load_builtins()
        return cls._instance
    
    def _load_builtins(self) -> None:
        """Load built-in taxonomies."""
        self._taxonomies["cybersecurity"] = get_cybersecurity_taxonomy()
    
    def register(self, taxonomy: TaxonomySpec) -> None:
        """Register a taxonomy specification."""
        self._taxonomies[taxonomy.name] = taxonomy
    
    def get(self, name: str) -> Optional[TaxonomySpec]:
        """Get a taxonomy by name."""
        return self._taxonomies.get(name)
    
    def list(self) -> List[str]:
        """List all registered taxonomy names."""
        return list(self._taxonomies.keys())
    
    def load_from_file(self, path: Union[str, Path]) -> TaxonomySpec:
        """
        Load a taxonomy from a YAML file.
        
        Args:
            path: Path to YAML taxonomy definition
            
        Returns:
            Loaded and registered TaxonomySpec
        """
        config_path = Path(path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Taxonomy file not found: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        taxonomy = TaxonomySpec.model_validate(data)
        self.register(taxonomy)
        return taxonomy
    
    def load_from_dict(self, data: Dict[str, Any]) -> TaxonomySpec:
        """Load a taxonomy from a dictionary."""
        taxonomy = TaxonomySpec.model_validate(data)
        self.register(taxonomy)
        return taxonomy
    
    def clear(self) -> None:
        """Clear all registered taxonomies (for testing)."""
        self._taxonomies.clear()
        self._load_builtins()


# Convenience functions
def get_taxonomy(name: str = "cybersecurity") -> Optional[TaxonomySpec]:
    """Get a taxonomy by name from the global registry."""
    return TaxonomyRegistry().get(name)


def list_taxonomies() -> List[str]:
    """List all registered taxonomy names."""
    return TaxonomyRegistry().list()


def register_taxonomy(taxonomy: TaxonomySpec) -> None:
    """Register a taxonomy in the global registry."""
    TaxonomyRegistry().register(taxonomy)


