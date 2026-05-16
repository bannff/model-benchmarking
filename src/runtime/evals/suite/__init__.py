from .loader import SuiteLoader
from .errors import SuiteLoadError
from typing import Union, Dict, Any, Optional
from pathlib import Path
from ..models import SuiteSpec

def load_suite(
    path: Union[str, Path],
    overrides: Optional[Dict[str, Any]] = None,
) -> Any:
    """Convenience function to load a suite configuration."""
    return SuiteLoader.load(path, overrides)

__all__ = ["SuiteLoader", "SuiteLoadError", "load_suite"]
