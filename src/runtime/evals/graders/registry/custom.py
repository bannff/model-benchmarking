"""
Custom grader implementation and loading logic.
"""
from __future__ import annotations

import importlib
import importlib.util
from typing import Any, Callable, Dict, Optional, Type

from ...models import Sample, GradeResult, ExtractorSpec
from ..base import BaseGrader, GraderError

def load_custom_grader(module_path: str) -> Callable[..., GradeResult]:
    """
    Load a custom grader from a module path.
    """
    if ":" not in module_path:
        raise GraderError(
            f"Invalid module path: '{module_path}'. Expected 'module:function' format."
        )
    
    module_name, func_name = module_path.rsplit(":", 1)
    
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        import sys
        from pathlib import Path
        
        file_path = Path(module_name)
        if file_path.suffix == ".py" and file_path.exists():
            spec = importlib.util.spec_from_file_location("custom_grader", file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules["custom_grader"] = module
                spec.loader.exec_module(module)
            else:
                raise GraderError(f"Could not load module from {file_path}")
        else:
            raise GraderError(f"Module not found: {module_name}")
    
    if not hasattr(module, func_name):
        raise GraderError(f"Function '{func_name}' not found in module '{module_name}'")
    
    return getattr(module, func_name)


class FunctionGrader(BaseGrader):
    """
    Grader wrapping a custom function.
    """
    def __init__(
        self,
        func: Callable[..., GradeResult],
        extractor: Optional[ExtractorSpec] = None,
        config: Optional[Dict[str, Any]] = None,
        display_name: Optional[str] = None,
    ):
        super().__init__(extractor=extractor, display_name=display_name)
        self.func = func
        self.config = config or {}
    
    async def grade(
        self,
        sample: Sample,
        submission: str,
        **kwargs: Any,
    ) -> GradeResult:
        result = self.func(
            submission,
            sample.ground_truth or "",
            self.config,
            sample,
        )
        
        if isinstance(result, GradeResult):
            return result
        elif isinstance(result, dict):
            return GradeResult.model_validate(result)
        elif isinstance(result, (int, float)):
            return GradeResult(score=float(result))
        else:
            raise GraderError(
                f"Custom grader must return GradeResult, dict, or float. Got: {type(result)}"
            )
