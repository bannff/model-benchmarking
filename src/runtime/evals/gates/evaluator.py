"""
Gate evaluation for pass/fail criteria.
"""
from __future__ import annotations

from typing import List, Optional

from ..models import (
    GateSpec,
    GateOperator,
    Aggregation,
    SampleResult,
)


class GateError(Exception):
    """Error evaluating a gate."""
    pass


class GateEvaluator:
    """Evaluates pass/fail gates against evaluation results."""
    
    def __init__(self, spec: GateSpec):
        self.spec = spec
    
    def _aggregate_scores(
        self,
        scores: List[float],
        aggregation: Aggregation,
        pass_threshold: Optional[float] = None,
    ) -> float:
        if not scores:
            return 0.0
        if aggregation == Aggregation.AVG:
            return sum(scores) / len(scores)
        if aggregation == Aggregation.MIN:
            return min(scores)
        if aggregation == Aggregation.MAX:
            return max(scores)
        if aggregation == Aggregation.MEDIAN:
            sorted_scores = sorted(scores)
            n = len(sorted_scores)
            mid = n // 2
            return (sorted_scores[mid - 1] + sorted_scores[mid]) / 2 if n % 2 == 0 else sorted_scores[mid]
        if aggregation == Aggregation.ACCURACY:
            threshold = pass_threshold if pass_threshold is not None else 1.0
            return sum(1 for s in scores if s >= threshold) / len(scores)
        if aggregation == Aggregation.PASS_RATE:
            return sum(1 for s in scores if s == 1.0) / len(scores)
        raise GateError(f"Unknown aggregation method: {aggregation}")

    def _compare(self, value: float, threshold: float, op: GateOperator) -> bool:
        if op == GateOperator.GTE: return value >= threshold
        if op == GateOperator.GT: return value > threshold
        if op == GateOperator.LTE: return value <= threshold
        if op == GateOperator.LT: return value < threshold
        if op == GateOperator.EQ: return abs(value - threshold) < 1e-9
        raise GateError(f"Unknown operator: {op}")

    def _get_scores(self, results: List[SampleResult], metric_key: str) -> List[float]:
        scores = []
        for result in results:
            if result.error: continue
            if metric_key == "default": scores.append(result.grade.score)
            elif result.grades and metric_key in result.grades: scores.append(result.grades[metric_key].score)
            else: scores.append(result.grade.score)
        return scores

    def evaluate(self, results: List[SampleResult]) -> tuple[bool, str]:
        scores = self._get_scores(results, self.spec.metric_key)
        if not scores: return False, "No valid scores to evaluate"
        aggregated = self._aggregate_scores(scores, self.spec.aggregation, self.spec.pass_threshold)
        passed = self._compare(aggregated, self.spec.value, self.spec.op)
        op_symbol = {GateOperator.GTE: ">=", GateOperator.GT: ">", GateOperator.LTE: "<=", GateOperator.LT: "<", GateOperator.EQ: "=="}[self.spec.op]
        details = f"Gate: {self.spec.metric_key} ({self.spec.aggregation.value}) = {aggregated:.4f} {op_symbol} {self.spec.value} → {'PASSED' if passed else 'FAILED'}"
        return passed, details
