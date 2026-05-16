"""
Registry for extractor implementations.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Type
from .base import BaseExtractor, ExtractorError
from ..models import ExtractorSpec
from . import builtins


class ExtractorRegistry:
    """Registry for extractor implementations."""
    
    _extractors: Dict[str, Type[BaseExtractor]] = {
        "last_assistant": builtins.LastAssistantExtractor,
        "all_text": builtins.AllTextExtractor,
        "json_field": builtins.JsonFieldExtractor,
        "regex": builtins.RegexCaptureExtractor,
        "regex_capture": builtins.RegexCaptureExtractor,
        "tool_calls": builtins.ToolCallsExtractor,
        "first_line": builtins.FirstLineExtractor,
        "code_block": builtins.CodeBlockExtractor,
    }
    
    @classmethod
    def register(cls, name: str, extractor_class: Type[BaseExtractor]) -> None:
        cls._extractors[name] = extractor_class
    
    @classmethod
    def get(cls, name: str) -> Type[BaseExtractor]:
        if name not in cls._extractors:
            available = ", ".join(sorted(cls._extractors.keys()))
            raise ExtractorError(f"Unknown extractor: '{name}'. Available: {available}")
        return cls._extractors[name]
    
    @classmethod
    def create(cls, spec: ExtractorSpec) -> BaseExtractor:
        return cls.get(spec.name)(config=spec.config)


def get_extractor(spec: ExtractorSpec) -> BaseExtractor:
    return ExtractorRegistry.create(spec)


def extractor(func: Optional[Callable] = None, *, name: Optional[str] = None):
    """Decorator to register a function as a custom extractor."""
    def decorator(fn: Callable) -> Callable:
        extractor_name = name or fn.__name__
        class FunctionExtractor(BaseExtractor):
            def extract(self, response: str, **kwargs: Any) -> str:
                return fn(response, self.config, **kwargs)
        FunctionExtractor.__name__ = f"{extractor_name}Extractor"
        ExtractorRegistry.register(extractor_name, FunctionExtractor)
        return fn
    return decorator(func) if func is not None else decorator
