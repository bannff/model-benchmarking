"""
Extractors for parsing model responses.

Extractors take raw model output and extract the relevant portion for grading.
Built-in extractors:
- last_assistant: Final assistant message (for chat completions)
- all_text: Full response text
- json_field: Parse JSON and extract a specific field
- regex_capture: Extract text matching a regex pattern
- tool_calls: Extract tool/function call information

Custom extractors can be registered using the @extractor decorator.
"""
from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type

from .models import ExtractorSpec


class ExtractorError(Exception):
    """Error during extraction."""
    pass


class BaseExtractor(ABC):
    """Base class for extractors."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    @abstractmethod
    def extract(self, response: str, **kwargs: Any) -> str:
        """
        Extract the relevant portion from a response.
        
        Args:
            response: Raw model response
            **kwargs: Additional context (sample, trajectory, etc.)
        
        Returns:
            Extracted submission string
        """
        pass


class LastAssistantExtractor(BaseExtractor):
    """
    Extract the last assistant message.
    
    For plain text responses, returns the full response.
    For structured chat responses, extracts the last assistant turn.
    """
    
    def extract(self, response: str, **kwargs: Any) -> str:
        # For plain text, return as-is
        response = response.strip()
        
        # Try to detect and handle common chat formats
        # Format: "Assistant: <message>"
        pattern = r"(?:assistant|AI|model):\s*(.+?)(?:\n(?:user|human|User|Human):|$)"
        matches = re.findall(pattern, response, re.IGNORECASE | re.DOTALL)
        if matches:
            return matches[-1].strip()
        
        return response


class AllTextExtractor(BaseExtractor):
    """Return the full response text."""
    
    def extract(self, response: str, **kwargs: Any) -> str:
        return response.strip()


class JsonFieldExtractor(BaseExtractor):
    """
    Parse response as JSON and extract a specific field.
    
    Config:
        field: The field name to extract (supports dot notation: "result.answer")
        default: Default value if field not found (default: "")
    """
    
    def extract(self, response: str, **kwargs: Any) -> str:
        field = self.config.get("field", "answer")
        default = self.config.get("default", "")
        
        # Try to find JSON in the response
        response = response.strip()
        
        # Handle markdown code blocks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response)
        if json_match:
            response = json_match.group(1).strip()
        
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            obj_match = re.search(r"\{[\s\S]*\}", response)
            if obj_match:
                try:
                    data = json.loads(obj_match.group())
                except json.JSONDecodeError:
                    return str(default)
            else:
                return str(default)
        
        # Navigate dot-notation path
        parts = field.split(".")
        for part in parts:
            if isinstance(data, dict) and part in data:
                data = data[part]
            elif isinstance(data, list) and part.isdigit():
                idx = int(part)
                if 0 <= idx < len(data):
                    data = data[idx]
                else:
                    return str(default)
            else:
                return str(default)
        
        return str(data) if data is not None else str(default)


class RegexCaptureExtractor(BaseExtractor):
    """
    Extract text matching a regex pattern.
    
    Config:
        pattern: Regex pattern with capturing groups
        group: Which group to return (default: 1, or 0 for full match)
        default: Default value if no match (default: "")
        flags: Regex flags string (e.g., "i" for case-insensitive)
    """
    
    def extract(self, response: str, **kwargs: Any) -> str:
        pattern = self.config.get("pattern", "(.+)")
        group = self.config.get("group", 1)
        default = self.config.get("default", "")
        flags_str = self.config.get("flags", "")
        
        # Parse flags
        flags = 0
        if "i" in flags_str:
            flags |= re.IGNORECASE
        if "m" in flags_str:
            flags |= re.MULTILINE
        if "s" in flags_str:
            flags |= re.DOTALL
        
        try:
            match = re.search(pattern, response, flags)
            if match:
                try:
                    return match.group(group)
                except IndexError:
                    return match.group(0)
            return str(default)
        except re.error as e:
            raise ExtractorError(f"Invalid regex pattern: {e}")


class ToolCallsExtractor(BaseExtractor):
    """
    Extract tool/function call information from response.
    
    Config:
        tool_name: Filter to specific tool (optional)
        extract: What to extract - "names", "arguments", "all" (default: "all")
    """
    
    def extract(self, response: str, **kwargs: Any) -> str:
        tool_name_filter = self.config.get("tool_name")
        extract_type = self.config.get("extract", "all")
        
        # Try to find tool calls in common formats
        tool_calls: List[Dict[str, Any]] = []
        
        # Format: <tool_call>{"name": "...", "arguments": {...}}</tool_call>
        xml_pattern = r"<tool_call[^>]*>([\s\S]*?)</tool_call>"
        for match in re.finditer(xml_pattern, response):
            try:
                call = json.loads(match.group(1))
                tool_calls.append(call)
            except json.JSONDecodeError:
                pass
        
        # Format: ```tool_call\n{...}\n```
        code_pattern = r"```tool_call\s*([\s\S]*?)```"
        for match in re.finditer(code_pattern, response):
            try:
                call = json.loads(match.group(1))
                tool_calls.append(call)
            except json.JSONDecodeError:
                pass
        
        # Filter by tool name
        if tool_name_filter:
            tool_calls = [
                tc for tc in tool_calls
                if tc.get("name") == tool_name_filter
            ]
        
        # Extract requested info
        if extract_type == "names":
            return ", ".join(tc.get("name", "") for tc in tool_calls)
        elif extract_type == "arguments":
            args = [tc.get("arguments", {}) for tc in tool_calls]
            return json.dumps(args)
        else:
            return json.dumps(tool_calls)


class FirstLineExtractor(BaseExtractor):
    """Extract just the first line of the response."""
    
    def extract(self, response: str, **kwargs: Any) -> str:
        lines = response.strip().split("\n")
        return lines[0].strip() if lines else ""


class CodeBlockExtractor(BaseExtractor):
    """
    Extract code from markdown code blocks.
    
    Config:
        language: Filter to specific language (optional)
        index: Which block to extract, 0-indexed (default: 0)
    """
    
    def extract(self, response: str, **kwargs: Any) -> str:
        language = self.config.get("language")
        index = self.config.get("index", 0)
        
        if language:
            pattern = rf"```{language}\s*([\s\S]*?)```"
        else:
            pattern = r"```(?:\w+)?\s*([\s\S]*?)```"
        
        matches = re.findall(pattern, response, re.IGNORECASE)
        
        if matches and 0 <= index < len(matches):
            return matches[index].strip()
        
        return ""


# -----------------------------------------------------------------------------
# Registry
# -----------------------------------------------------------------------------


class ExtractorRegistry:
    """Registry for extractor implementations."""
    
    _extractors: Dict[str, Type[BaseExtractor]] = {
        "last_assistant": LastAssistantExtractor,
        "all_text": AllTextExtractor,
        "json_field": JsonFieldExtractor,
        "regex": RegexCaptureExtractor,
        "regex_capture": RegexCaptureExtractor,
        "tool_calls": ToolCallsExtractor,
        "first_line": FirstLineExtractor,
        "code_block": CodeBlockExtractor,
    }
    
    @classmethod
    def register(cls, name: str, extractor_class: Type[BaseExtractor]) -> None:
        """Register a custom extractor."""
        cls._extractors[name] = extractor_class
    
    @classmethod
    def get(cls, name: str) -> Type[BaseExtractor]:
        """Get an extractor class by name."""
        if name not in cls._extractors:
            available = ", ".join(sorted(cls._extractors.keys()))
            raise ExtractorError(
                f"Unknown extractor: '{name}'. Available: {available}"
            )
        return cls._extractors[name]
    
    @classmethod
    def list_extractors(cls) -> List[str]:
        """List all registered extractor names."""
        return sorted(cls._extractors.keys())
    
    @classmethod
    def create(cls, spec: ExtractorSpec) -> BaseExtractor:
        """Create an extractor instance from a spec."""
        extractor_class = cls.get(spec.name)
        return extractor_class(config=spec.config)


def get_extractor(spec: ExtractorSpec) -> BaseExtractor:
    """Create an extractor from a spec (convenience function)."""
    return ExtractorRegistry.create(spec)


def extractor(func: Optional[Callable] = None, *, name: Optional[str] = None):
    """
    Decorator to register a function as a custom extractor.
    
    Usage:
        @extractor
        def my_extractor(response: str, config: dict) -> str:
            return response.upper()
        
        @extractor(name="custom_name")
        def another_extractor(response: str, config: dict) -> str:
            return response.lower()
    """
    def decorator(fn: Callable) -> Callable:
        extractor_name = name or fn.__name__
        
        # Create a wrapper class
        class FunctionExtractor(BaseExtractor):
            def extract(self, response: str, **kwargs: Any) -> str:
                return fn(response, self.config, **kwargs)
        
        FunctionExtractor.__name__ = f"{extractor_name}Extractor"
        ExtractorRegistry.register(extractor_name, FunctionExtractor)
        return fn
    
    if func is not None:
        return decorator(func)
    return decorator
