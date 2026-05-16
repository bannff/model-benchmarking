"""
Built-in extractor implementations.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from .base import BaseExtractor


class LastAssistantExtractor(BaseExtractor):
    """Extract the last assistant message."""
    def extract(self, response: str, **kwargs: Any) -> str:
        response = response.strip()
        pattern = r"(?:assistant|AI|model):\s*(.+?)(?:\n(?:user|human|User|Human):|$)"
        matches = re.findall(pattern, response, re.IGNORECASE | re.DOTALL)
        return matches[-1].strip() if matches else response


class AllTextExtractor(BaseExtractor):
    """Return the full response text."""
    def extract(self, response: str, **kwargs: Any) -> str:
        return response.strip()


class JsonFieldExtractor(BaseExtractor):
    """Parse response as JSON and extract a specific field."""
    def extract(self, response: str, **kwargs: Any) -> str:
        field = self.config.get("field", "answer")
        default = self.config.get("default", "")
        response = response.strip()
        
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response)
        if json_match: response = json_match.group(1).strip()
        
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            obj_match = re.search(r"\{[\s\S]*\}", response)
            if obj_match:
                try: data = json.loads(obj_match.group())
                except json.JSONDecodeError: return str(default)
            else: return str(default)
        
        for part in field.split("."):
            if isinstance(data, dict) and part in data: data = data[part]
            elif isinstance(data, list) and part.isdigit():
                idx = int(part)
                data = data[idx] if 0 <= idx < len(data) else default
            else: return str(default)
        return str(data) if data is not None else str(default)


class RegexCaptureExtractor(BaseExtractor):
    """Extract text matching a regex pattern."""
    def extract(self, response: str, **kwargs: Any) -> str:
        pattern = self.config.get("pattern", "(.+)")
        group = self.config.get("group", 1)
        default = self.config.get("default", "")
        flags_str = self.config.get("flags", "")
        
        flags = 0
        if "i" in flags_str: flags |= re.IGNORECASE
        if "m" in flags_str: flags |= re.MULTILINE
        if "s" in flags_str: flags |= re.DOTALL
        
        try:
            match = re.search(pattern, response, flags)
            if match:
                try: return match.group(group)
                except IndexError: return match.group(0)
            return str(default)
        except re.error as e:
            from .base import ExtractorError
            raise ExtractorError(f"Invalid regex pattern: {e}")


class ToolCallsExtractor(BaseExtractor):
    """Extract tool/function call information from response."""
    def extract(self, response: str, **kwargs: Any) -> str:
        tool_name_filter = self.config.get("tool_name")
        extract_type = self.config.get("extract", "all")
        tool_calls: List[Dict[str, Any]] = []
        
        for pattern in (r"<tool_call[^>]*>([\s\S]*?)</tool_call>", r"```tool_call\s*([\s\S]*?)```"):
            for match in re.finditer(pattern, response):
                try: tool_calls.append(json.loads(match.group(1)))
                except json.JSONDecodeError: pass
        
        if tool_name_filter:
            tool_calls = [tc for tc in tool_calls if tc.get("name") == tool_name_filter]
        
        if extract_type == "names": return ", ".join(tc.get("name", "") for tc in tool_calls)
        if extract_type == "arguments": return json.dumps([tc.get("arguments", {}) for tc in tool_calls])
        return json.dumps(tool_calls)


class FirstLineExtractor(BaseExtractor):
    """Extract just the first line of the response."""
    def extract(self, response: str, **kwargs: Any) -> str:
        lines = response.strip().split("\n")
        return lines[0].strip() if lines else ""


class CodeBlockExtractor(BaseExtractor):
    """Extract code from markdown code blocks."""
    def extract(self, response: str, **kwargs: Any) -> str:
        language = self.config.get("language")
        index = self.config.get("index", 0)
        pattern = rf"```{language}\s*([\s\S]*?)```" if language else r"```(?:\w+)?\s*([\s\S]*?)```"
        matches = re.findall(pattern, response, re.IGNORECASE)
        return matches[index].strip() if matches and 0 <= index < len(matches) else ""
