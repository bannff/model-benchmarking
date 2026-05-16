"""
Grader registry and factory entry point.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Type

from runtime.evals.models import GraderSpec, GradeResult
from runtime.evals.graders.base import BaseGrader
from runtime.evals.graders.tool_graders import TOOL_GRADER_FUNCTIONS
from runtime.utils.registry import Registry

function_registry = Registry[GradeResult]("grader_functions")


class GraderRegistry:
	"""Registry for grader implementations."""

	_graders: Dict[str, Type[BaseGrader]] = {}

	@classmethod
	def register(cls, name: str, grader_class: Type[BaseGrader]) -> None:
		cls._graders[name] = grader_class

	@classmethod
	def register_function(cls, name: str, func: Callable[..., GradeResult]) -> None:
		function_registry.register(name)(func)

	@classmethod
	def get(cls, name: str) -> Optional[Type[BaseGrader]]:
		return cls._graders.get(name)

	@classmethod
	def get_function(cls, name: str) -> Optional[Callable[..., GradeResult]]:
		return function_registry.get(name)  # type: ignore[return-value]

	@classmethod
	def list_graders(cls) -> Dict[str, str]:
		result = {}
		for name, cls_obj in cls._graders.items():
			result[name] = f"Class: {cls_obj.__name__}"
		for name in function_registry.list_keys():
			func = function_registry.get(name)
			doc = func.__doc__ or "Custom function" if func else "Custom function"
			result[name] = doc.split("\n")[0]
		return result

	@classmethod
	def list_tool_functions(cls) -> Dict[str, str]:
		result = {}
		for name, func in TOOL_GRADER_FUNCTIONS.items():
			doc = func.__doc__ or ""
			result[name] = doc.split("\n")[0].strip()
		return result


def grader(func: Optional[Callable[..., GradeResult]] = None, *, name: Optional[str] = None):
	"""Decorator to register a function as a custom grader."""

	def decorator(fn: Callable[..., GradeResult]) -> Callable[..., GradeResult]:
		grader_name = name or fn.__name__
		GraderRegistry.register_function(grader_name, fn)
		return fn

	if func is not None:
		return decorator(func)
	return decorator


# Proxy to factory to maintain legacy API
from .factory import get_grader
