"""
Base classes for extractors.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ExtractorError(Exception):
    """Error during extraction."""
    pass


class BaseExtractor(ABC):
    """Base class for extractors."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    @abstractmethod
    def extract(self, response: str, **kwargs: Any) -> str:
        """Extract the relevant portion from a response."""
        pass
