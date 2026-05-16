"""
Metric calculation for evaluation results.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from ..models import (
    SampleResult,
    Metrics,
    MetricAggregate,
)


def calculate_metrics(
    results: List[SampleResult],
    grader_keys: Optional[List[str]] = None,
) -> Metrics:
    """Calculate aggregate metrics from results."""
    total = len(results)
    attempted = sum(1 for r in results if not r.error)
    failed = total - attempted
    
    scores = [r.grade.score for r in results if not r.error]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    pass_rate = sum(1 for s in scores if s == 1.0) / len(scores) if scores else 0.0
    
    by_metric: Dict[str, MetricAggregate] = {}
    if grader_keys:
        for key in grader_keys:
            metric_scores = [r.grades[key].score if (r.grades and key in r.grades) else r.grade.score 
                             for r in results if not r.error and (key == "default" or (r.grades and key in r.grades))]
            if metric_scores:
                by_metric[key] = MetricAggregate(
                    avg_score=sum(metric_scores) / len(metric_scores),
                    min_score=min(metric_scores),
                    max_score=max(metric_scores),
                    pass_rate=sum(1 for s in metric_scores if s == 1.0) / len(metric_scores),
                    count=len(metric_scores),
                )
    
    by_tag: Dict[str, MetricAggregate] = {}
    tag_scores: Dict[str, List[float]] = {}
    for r in results:
        if r.error: continue
        for tag in r.sample.tags:
            tag_scores.setdefault(tag, []).append(r.grade.score)
    
    for tag, s_list in tag_scores.items():
        by_tag[tag] = MetricAggregate(
            avg_score=sum(s_list) / len(s_list),
            min_score=min(s_list),
            max_score=max(s_list),
            pass_rate=sum(1 for s in s_list if s == 1.0) / len(s_list),
            count=len(s_list),
        )
    
    by_taxonomy: Dict[str, Dict[str, MetricAggregate]] = {}
    tax_scores: Dict[str, Dict[str, List[float]]] = {}
    for r in results:
        if r.error or not r.sample.taxonomy: continue
        for dim, values in r.sample.taxonomy.items():
            val_list = [values] if isinstance(values, str) else values
            for val in val_list:
                tax_scores.setdefault(dim, {}).setdefault(val, []).append(r.grade.score)
    
    for dim, val_map in tax_scores.items():
        by_taxonomy[dim] = {
            val: MetricAggregate(
                avg_score=sum(sl) / len(sl), min_score=min(sl), max_score=max(sl),
                pass_rate=sum(1 for s in sl if s == 1.0) / len(sl), count=len(sl)
            ) for val, sl in val_map.items()
        }
    
    return Metrics(
        total=total, attempted=attempted, failed=failed,
        avg_score=avg_score, pass_rate=pass_rate,
        by_metric=by_metric, by_tag=by_tag, by_taxonomy=by_taxonomy,
    )
