"""
Gate evaluation for pass/fail criteria.

Gates define thresholds that evaluation results must meet to "pass".
Supports various aggregation methods and comparison operators.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import (
    GateSpec,
    GateOperator,
    Aggregation,
    SampleResult,
    Metrics,
    MetricAggregate,
)


class GateError(Exception):
    """Error evaluating a gate."""
    pass


class GateEvaluator:
    """
    Evaluates pass/fail gates against evaluation results.
    
    Usage:
        gate = GateSpec(metric_key="accuracy", op="gte", value=0.8)
        evaluator = GateEvaluator(gate)
        passed, details = evaluator.evaluate(results)
    """
    
    def __init__(self, spec: GateSpec):
        self.spec = spec
    
    def _aggregate_scores(
        self,
        scores: List[float],
        aggregation: Aggregation,
        pass_threshold: Optional[float] = None,
    ) -> float:
        """Aggregate a list of scores using the specified method."""
        if not scores:
            return 0.0
        
        if aggregation == Aggregation.AVG:
            return sum(scores) / len(scores)
        
        elif aggregation == Aggregation.MIN:
            return min(scores)
        
        elif aggregation == Aggregation.MAX:
            return max(scores)
        
        elif aggregation == Aggregation.MEDIAN:
            sorted_scores = sorted(scores)
            n = len(sorted_scores)
            mid = n // 2
            if n % 2 == 0:
                return (sorted_scores[mid - 1] + sorted_scores[mid]) / 2
            return sorted_scores[mid]
        
        elif aggregation == Aggregation.ACCURACY:
            # Percentage of scores >= threshold
            threshold = pass_threshold if pass_threshold is not None else 1.0
            passed = sum(1 for s in scores if s >= threshold)
            return passed / len(scores)
        
        elif aggregation == Aggregation.PASS_RATE:
            # Percentage of perfect scores (1.0)
            passed = sum(1 for s in scores if s == 1.0)
            return passed / len(scores)
        
        else:
            raise GateError(f"Unknown aggregation method: {aggregation}")
    
    def _compare(self, value: float, threshold: float, op: GateOperator) -> bool:
        """Compare a value against a threshold using the specified operator."""
        if op == GateOperator.GTE:
            return value >= threshold
        elif op == GateOperator.GT:
            return value > threshold
        elif op == GateOperator.LTE:
            return value <= threshold
        elif op == GateOperator.LT:
            return value < threshold
        elif op == GateOperator.EQ:
            return abs(value - threshold) < 1e-9
        else:
            raise GateError(f"Unknown operator: {op}")
    
    def _get_scores(
        self,
        results: List[SampleResult],
        metric_key: str,
    ) -> List[float]:
        """Extract scores for a specific metric from results."""
        scores = []
        
        for result in results:
            # Skip failed evaluations
            if result.error:
                continue
            
            if metric_key == "default":
                # Use the primary grade
                scores.append(result.grade.score)
            elif result.grades and metric_key in result.grades:
                # Use the specific metric
                scores.append(result.grades[metric_key].score)
            else:
                # Fall back to primary grade if metric not found
                scores.append(result.grade.score)
        
        return scores
    
    def evaluate(
        self,
        results: List[SampleResult],
    ) -> tuple[bool, str]:
        """
        Evaluate the gate against results.
        
        Args:
            results: List of sample results
        
        Returns:
            Tuple of (passed: bool, details: str)
        """
        scores = self._get_scores(results, self.spec.metric_key)
        
        if not scores:
            return False, "No valid scores to evaluate"
        
        aggregated = self._aggregate_scores(
            scores,
            self.spec.aggregation,
            self.spec.pass_threshold,
        )
        
        passed = self._compare(aggregated, self.spec.value, self.spec.op)
        
        op_symbol = {
            GateOperator.GTE: ">=",
            GateOperator.GT: ">",
            GateOperator.LTE: "<=",
            GateOperator.LT: "<",
            GateOperator.EQ: "==",
        }[self.spec.op]
        
        details = (
            f"Gate: {self.spec.metric_key} "
            f"({self.spec.aggregation.value}) = {aggregated:.4f} "
            f"{op_symbol} {self.spec.value} → "
            f"{'PASSED' if passed else 'FAILED'}"
        )
        
        return passed, details
    
    def evaluate_metrics(
        self,
        metrics: Metrics,
    ) -> tuple[bool, str]:
        """
        Evaluate the gate against pre-computed metrics.
        
        Args:
            metrics: Aggregate metrics
        
        Returns:
            Tuple of (passed: bool, details: str)
        """
        # Get the appropriate value based on metric_key
        if self.spec.metric_key == "default":
            if self.spec.aggregation == Aggregation.AVG:
                value = metrics.avg_score
            elif self.spec.aggregation == Aggregation.PASS_RATE:
                value = metrics.pass_rate
            else:
                # For other aggregations, we'd need the raw scores
                value = metrics.avg_score
        elif self.spec.metric_key in metrics.by_metric:
            agg = metrics.by_metric[self.spec.metric_key]
            value = agg.avg_score
        else:
            return False, f"Metric '{self.spec.metric_key}' not found"
        
        passed = self._compare(value, self.spec.value, self.spec.op)
        
        op_symbol = {
            GateOperator.GTE: ">=",
            GateOperator.GT: ">",
            GateOperator.LTE: "<=",
            GateOperator.LT: "<",
            GateOperator.EQ: "==",
        }[self.spec.op]
        
        details = (
            f"Gate: {self.spec.metric_key} = {value:.4f} "
            f"{op_symbol} {self.spec.value} → "
            f"{'PASSED' if passed else 'FAILED'}"
        )
        
        return passed, details


def check_gate(
    gate: GateSpec,
    results: List[SampleResult],
) -> tuple[bool, str]:
    """
    Convenience function to check a gate against results.
    
    Args:
        gate: Gate specification
        results: List of sample results
    
    Returns:
        Tuple of (passed: bool, details: str)
    """
    evaluator = GateEvaluator(gate)
    return evaluator.evaluate(results)


def calculate_metrics(
    results: List[SampleResult],
    grader_keys: Optional[List[str]] = None,
) -> Metrics:
    """
    Calculate aggregate metrics from results.
    
    Args:
        results: List of sample results
        grader_keys: List of grader/metric keys (optional)
    
    Returns:
        Metrics object with aggregated statistics
    """
    total = len(results)
    attempted = sum(1 for r in results if not r.error)
    failed = total - attempted
    
    # Overall scores
    scores = [r.grade.score for r in results if not r.error]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    pass_rate = sum(1 for s in scores if s == 1.0) / len(scores) if scores else 0.0
    
    # Per-metric aggregates
    by_metric: Dict[str, MetricAggregate] = {}
    
    if grader_keys:
        for key in grader_keys:
            metric_scores = []
            for r in results:
                if r.error:
                    continue
                if r.grades and key in r.grades:
                    metric_scores.append(r.grades[key].score)
                elif key == "default":
                    metric_scores.append(r.grade.score)
            
            if metric_scores:
                by_metric[key] = MetricAggregate(
                    avg_score=sum(metric_scores) / len(metric_scores),
                    min_score=min(metric_scores),
                    max_score=max(metric_scores),
                    pass_rate=sum(1 for s in metric_scores if s == 1.0) / len(metric_scores),
                    count=len(metric_scores),
                )
    
    # Per-tag aggregates
    by_tag: Dict[str, MetricAggregate] = {}
    tag_scores: Dict[str, List[float]] = {}
    
    for r in results:
        if r.error:
            continue
        for tag in r.sample.tags:
            if tag not in tag_scores:
                tag_scores[tag] = []
            tag_scores[tag].append(r.grade.score)
    
    for tag, scores_list in tag_scores.items():
        by_tag[tag] = MetricAggregate(
            avg_score=sum(scores_list) / len(scores_list),
            min_score=min(scores_list),
            max_score=max(scores_list),
            pass_rate=sum(1 for s in scores_list if s == 1.0) / len(scores_list),
            count=len(scores_list),
        )
    
    # Per-taxonomy dimension aggregates
    by_taxonomy: Dict[str, Dict[str, MetricAggregate]] = {}
    taxonomy_scores: Dict[str, Dict[str, List[float]]] = {}
    
    for r in results:
        if r.error:
            continue
        if r.sample.taxonomy:
            for dim, values in r.sample.taxonomy.items():
                if dim not in taxonomy_scores:
                    taxonomy_scores[dim] = {}
                
                # Normalize to list
                value_list = [values] if isinstance(values, str) else values
                
                for val in value_list:
                    if val not in taxonomy_scores[dim]:
                        taxonomy_scores[dim][val] = []
                    taxonomy_scores[dim][val].append(r.grade.score)
    
    for dim, val_scores in taxonomy_scores.items():
        by_taxonomy[dim] = {}
        for val, scores_list in val_scores.items():
            by_taxonomy[dim][val] = MetricAggregate(
                avg_score=sum(scores_list) / len(scores_list),
                min_score=min(scores_list),
                max_score=max(scores_list),
                pass_rate=sum(1 for s in scores_list if s == 1.0) / len(scores_list),
                count=len(scores_list),
            )
    
    return Metrics(
        total=total,
        attempted=attempted,
        failed=failed,
        avg_score=avg_score,
        pass_rate=pass_rate,
        by_metric=by_metric,
        by_tag=by_tag,
        by_taxonomy=by_taxonomy,
    )
