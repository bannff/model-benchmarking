"""
Evaluation runner and utilities.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .core import EvalRunner
from ..suite import load_suite
from ..models import RunnerResult


async def run_suite(
    suite_path: Union[str, Path],
    provider: Any,
    *,
    overrides: Optional[Dict[str, Any]] = None,
    verbose: bool = False,
) -> RunnerResult:
    """Load and run a suite from a YAML config file."""
    suite = load_suite(suite_path, overrides)
    runner = EvalRunner(suite, provider, verbose=verbose)
    return await runner.run()


def run_suite_sync(
    suite_path: Union[str, Path],
    provider: Any,
    *,
    overrides: Optional[Dict[str, Any]] = None,
    verbose: bool = False,
) -> RunnerResult:
    """Synchronous version of run_suite()."""
    return asyncio.run(run_suite(suite_path, provider, overrides=overrides, verbose=verbose))


__all__ = ["EvalRunner", "run_suite", "run_suite_sync"]
