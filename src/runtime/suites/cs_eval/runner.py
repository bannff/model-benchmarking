"""
Core runner for the CS-Eval benchmark suite.
Orchestrates dataset loading, provider interaction, and scoring.
"""
from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime.providers.base import BaseProvider
from .dataset import load_cs_eval_dataset
from .parser import parse_questions, filter_questions, CSEvalQuestion


async def run_cs_eval(
    provider: BaseProvider,
    categories: Optional[List[str]] = None,
    max_questions: Optional[int] = None,
    local_sample: Optional[str] = None,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Run the CS-Eval benchmark using the concurrent EvalRunner.
    """
    from ...evals.models import Sample, SuiteSpec, ToolGraderSpec, GateSpec, Aggregation, GateOperator
    from ...evals.runner.core import EvalRunner
    
    # 1. Load and parse questions
    raw_dataset = load_cs_eval_dataset(local_path=local_sample, verbose=verbose)
    all_questions = parse_questions(raw_dataset, verbose=verbose)
    target_questions = filter_questions(all_questions, categories, max_questions)
    
    if verbose:
        print(f"🚀 Running CS-Eval on {len(target_questions)} questions...")

    # 2. Map to Samples
    samples = []
    for q in target_questions:
        samples.append(Sample(
            id=q.id,
            input=q.question,
            ground_truth=q.answer,
            metadata={
                "category": q.category,
                "subcategory": q.subcategory,
                "options": q.options,
                "question_type": q.question_type
            }
        ))
    
    # 3. Construct a virtual SuiteSpec for EvalRunner
    spec = SuiteSpec(
        name="cs-eval",
        dataset=local_sample or "memory",
        graders={
            "default": ToolGraderSpec(function="exact_match")
        },
        gate=GateSpec(
            metric_key="default",
            aggregation=Aggregation.AVG,
            op=GateOperator.GTE,
            value=0.0
        ),
        max_concurrent=10
    )
    
    # 4. Run via concurrent EvalRunner
    runner = EvalRunner(spec, provider, verbose=verbose)
    runner_result = await runner.run(samples=samples)
    
    # 5. Map back to legacy format for reporting compatibility
    results = []
    correct_count = 0
    for r in runner_result.results:
        is_correct = r.grade.score >= 1.0
        if is_correct:
            correct_count += 1
            
        results.append({
            "id": r.sample.id,
            "category": r.sample.metadata.get("category"),
            "subcategory": r.sample.metadata.get("subcategory"),
            "question": r.sample.input,
            "options": r.sample.metadata.get("options"),
            "expected": r.sample.ground_truth,
            "predicted": r.submission,
            "is_correct": is_correct,
            "raw_response": r.response
        })
    
    return {
        "suite": "cs_eval",
        "timestamp": runner_result.started_at,
        "duration_seconds": (
            datetime.fromisoformat(runner_result.finished_at.replace("Z", "+00:00")) - 
            datetime.fromisoformat(runner_result.started_at.replace("Z", "+00:00"))
        ).total_seconds(),
        "metrics": {
            "total": len(results),
            "correct": correct_count,
            "accuracy": correct_count / len(results) if results else 0.0
        },
        "results": results
    }
