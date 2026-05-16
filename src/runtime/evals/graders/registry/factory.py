"""
Factory for creating graders from specifications.
"""
from __future__ import annotations

from typing import Any, Optional, Callable

from ...models import (
    GraderSpec,
    ToolGraderSpec,
    RubricGraderSpec,
    CustomGraderSpec,
    GradeResult,
)
from ..base import BaseGrader, GraderError
from ..tool_graders import ToolGrader
from ..rubric_grader import RubricGrader


def get_grader(
    spec: GraderSpec,
    base_dir: Optional[Any] = None,
) -> BaseGrader:
    """
    Create a grader instance from a spec.
    """
    if isinstance(spec, ToolGraderSpec):
        return ToolGrader(
            function=spec.function,
            extractor=spec.extractor,
            config=spec.config,
            display_name=spec.display_name,
        )
    
    elif isinstance(spec, RubricGraderSpec):
        return RubricGrader(
            prompt=spec.prompt,
            prompt_file=spec.prompt_file,
            model=spec.model,
            provider=spec.provider,
            temperature=spec.temperature,
            extractor=spec.extractor,
            rubric_vars=spec.rubric_vars,
            display_name=spec.display_name,
            base_dir=base_dir,
        )
    
    elif isinstance(spec, CustomGraderSpec):
        from .custom import FunctionGrader, load_custom_grader
        func = load_custom_grader(spec.module)
        return FunctionGrader(
            func=func,
            extractor=spec.extractor,
            config=spec.config,
            display_name=spec.display_name,
        )
    
    else:
        raise GraderError(f"Unknown grader spec type: {type(spec)}")
