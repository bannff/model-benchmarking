"""
Gate and metric utilities.
"""
from __future__ import annotations

from typing import List
from .evaluator import GateEvaluator, GateError
from .metrics import calculate_metrics
from ..models import GateSpec, SampleResult

def check_gate(
    gate: GateSpec,
    results: List[SampleResult],
) -> tuple[bool, str]:
    """Convenience function to check a gate against results."""
    evaluator = GateEvaluator(gate)
    return evaluator.evaluate(results)

__all__ = ["GateEvaluator", "GateError", "calculate_metrics", "check_gate"]
