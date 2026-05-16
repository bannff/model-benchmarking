"""
Graders package for scoring model outputs.

This package provides:
- ToolGrader: Fast, deterministic grading with functions like exact_match, contains, regex
- RubricGrader: LLM-as-judge grading with custom rubric prompts
- Custom graders via the @grader decorator
"""
from __future__ import annotations

from .base import BaseGrader, GraderError
from .tool_graders import ToolGrader, TOOL_GRADER_FUNCTIONS
from .rubric_grader import RubricGrader
from .registry import GraderRegistry, get_grader, grader

__all__ = [
    "BaseGrader",
    "GraderError",
    "ToolGrader",
    "TOOL_GRADER_FUNCTIONS",
    "RubricGrader",
    "GraderRegistry",
    "get_grader",
    "grader",
]
