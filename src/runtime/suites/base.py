"""
Suite interface for benchmark adapters.

Each suite should implement a small, consistent interface so the pipeline
can orchestrate them uniformly and we can unit test adapters in isolation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol


@dataclass
class SuiteOutcome:
    name: str
    status: str
    results_path: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class BaseSuite(Protocol):
    """Protocol for benchmark suites.

    Implementors should provide a `run` method that returns a SuiteOutcome.
    """

    name: str

    async def run(self, *, provider: Any, output_dir: str, **kwargs: Any) -> SuiteOutcome:
        ...
