"""
Tool-based graders for fast, deterministic scoring.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from ..models import GradeResult, Sample, ExtractorSpec
from .base import BaseGrader, GraderError
from . import functions

# Type for grader functions
GraderFunction = Callable[[str, str, Dict[str, Any]], GradeResult]

# Registry of built-in grader functions
TOOL_GRADER_FUNCTIONS: Dict[str, GraderFunction] = {
    "exact_match": functions.exact_match,
    "exact": functions.exact_match,
    "contains": functions.contains,
    "includes": functions.contains,
    "not_contains": functions.not_contains,
    "excludes": functions.not_contains,
    "regex": functions.regex_match,
    "regex_match": functions.regex_match,
    "starts_with": functions.starts_with,
    "ends_with": functions.ends_with,
    "numeric": functions.numeric_match,
    "numeric_match": functions.numeric_match,
    "json": functions.json_match,
    "json_match": functions.json_match,
    "length": functions.length_check,
    "length_check": functions.length_check,
}


class ToolGrader(BaseGrader):
    """
    Grader using deterministic tool functions.
    
    Usage:
        grader = ToolGrader(function="contains")
        result = grader.grade(sample, submission)
    """
    
    def __init__(
        self,
        function: str,
        extractor: Optional[ExtractorSpec] = None,
        config: Optional[Dict[str, Any]] = None,
        display_name: Optional[str] = None,
    ):
        super().__init__(extractor=extractor, display_name=display_name)
        
        if function not in TOOL_GRADER_FUNCTIONS:
            available = ", ".join(sorted(TOOL_GRADER_FUNCTIONS.keys()))
            raise GraderError(
                f"Unknown grader function: '{function}'. Available: {available}"
            )
        
        self.function_name = function
        self.grader_func = TOOL_GRADER_FUNCTIONS[function]
        self.config = config or {}
    
    async def grade(
        self,
        sample: Sample,
        submission: str,
        **kwargs: Any,
    ) -> GradeResult:
        """Grade using the configured tool function."""
        ground_truth = sample.ground_truth
        
        if ground_truth is None:
            raise GraderError(
                f"Tool grader '{self.function_name}' requires ground_truth in sample"
            )
        
        return self.grader_func(submission, ground_truth, self.config)
