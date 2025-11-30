"""
Grader registry and factory functions.

Provides:
- GraderRegistry: Central registry for grader classes
- get_grader: Factory function to create graders from specs
- @grader decorator: Register custom grader functions
"""
from __future__ import annotations

import importlib
from typing import Any, Callable, Dict, Optional, Type

from ..models import (
    GraderSpec,
    ToolGraderSpec,
    RubricGraderSpec,
    CustomGraderSpec,
    GradeResult,
    Sample,
    ExtractorSpec,
)
from .base import BaseGrader, GraderError
from .tool_graders import ToolGrader, TOOL_GRADER_FUNCTIONS
from .rubric_grader import RubricGrader


class GraderRegistry:
    """
    Registry for grader implementations.
    
    Stores both grader classes and custom grader functions.
    """
    
    _graders: Dict[str, Type[BaseGrader]] = {}
    _functions: Dict[str, Callable[..., GradeResult]] = {}
    
    @classmethod
    def register(
        cls,
        name: str,
        grader_class: Type[BaseGrader],
    ) -> None:
        """Register a grader class."""
        cls._graders[name] = grader_class
    
    @classmethod
    def register_function(
        cls,
        name: str,
        func: Callable[..., GradeResult],
    ) -> None:
        """Register a custom grader function."""
        cls._functions[name] = func
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseGrader]]:
        """Get a grader class by name."""
        return cls._graders.get(name)
    
    @classmethod
    def get_function(cls, name: str) -> Optional[Callable[..., GradeResult]]:
        """Get a custom grader function by name."""
        return cls._functions.get(name)
    
    @classmethod
    def list_graders(cls) -> Dict[str, str]:
        """List all registered graders with descriptions."""
        result = {}
        for name in cls._graders:
            result[name] = f"Class: {cls._graders[name].__name__}"
        for name in cls._functions:
            doc = cls._functions[name].__doc__ or "Custom function"
            result[name] = doc.split("\n")[0]
        return result
    
    @classmethod
    def list_tool_functions(cls) -> Dict[str, str]:
        """List all available tool grader functions."""
        result = {}
        for name, func in TOOL_GRADER_FUNCTIONS.items():
            doc = func.__doc__ or ""
            result[name] = doc.split("\n")[0].strip()
        return result


def _load_custom_grader(module_path: str) -> Callable[..., GradeResult]:
    """
    Load a custom grader from a module path.
    
    Format: "module.path:function_name" or "path/to/file.py:function_name"
    """
    if ":" not in module_path:
        raise GraderError(
            f"Invalid module path: '{module_path}'. Expected 'module:function' format."
        )
    
    module_name, func_name = module_path.rsplit(":", 1)
    
    try:
        # Try as a Python module first
        module = importlib.import_module(module_name)
    except ImportError:
        # Try as a file path
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


def get_grader(
    spec: GraderSpec,
    base_dir: Optional[Any] = None,
) -> BaseGrader:
    """
    Create a grader instance from a spec.
    
    Args:
        spec: Grader specification (ToolGraderSpec, RubricGraderSpec, or CustomGraderSpec)
        base_dir: Base directory for resolving relative paths
    
    Returns:
        Configured grader instance
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
        func = _load_custom_grader(spec.module)
        return FunctionGrader(
            func=func,
            extractor=spec.extractor,
            config=spec.config,
            display_name=spec.display_name,
        )
    
    else:
        raise GraderError(f"Unknown grader spec type: {type(spec)}")


class FunctionGrader(BaseGrader):
    """
    Grader wrapping a custom function.
    
    The function should have signature:
        def my_grader(submission: str, ground_truth: str, config: dict, sample: Sample) -> GradeResult
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
    
    def grade(
        self,
        sample: Sample,
        submission: str,
        **kwargs: Any,
    ) -> GradeResult:
        """Grade using the custom function."""
        result = self.func(
            submission,
            sample.ground_truth or "",
            self.config,
            sample,
        )
        
        # Ensure result is a GradeResult
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


def grader(
    func: Optional[Callable[..., GradeResult]] = None,
    *,
    name: Optional[str] = None,
):
    """
    Decorator to register a function as a custom grader.
    
    Usage:
        @grader
        def my_grader(submission: str, ground_truth: str, config: dict, sample: Sample) -> GradeResult:
            return GradeResult(score=1.0 if submission == ground_truth else 0.0)
        
        @grader(name="custom_name")
        def another_grader(...) -> GradeResult:
            ...
    """
    def decorator(fn: Callable[..., GradeResult]) -> Callable[..., GradeResult]:
        grader_name = name or fn.__name__
        GraderRegistry.register_function(grader_name, fn)
        return fn
    
    if func is not None:
        return decorator(func)
    return decorator
