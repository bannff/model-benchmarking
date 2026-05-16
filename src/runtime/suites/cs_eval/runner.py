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
    Run the CS-Eval benchmark.
    
    Returns:
        A dictionary containing scores, results, and metadata.
    """
    start_time = time.time()
    
    # Load and parse
    raw_dataset = load_cs_eval_dataset(local_path=local_sample, verbose=verbose)
    all_questions = parse_questions(raw_dataset, verbose=verbose)
    target_questions = filter_questions(all_questions, categories, max_questions)
    
    if verbose:
        print(f"🚀 Running CS-Eval on {len(target_questions)} questions...")

    results = []
    correct_count = 0
    
    for i, q in enumerate(target_questions):
        # Interact with model
        resp = provider.evaluate_question(
            question=q.question,
            options=q.options,
            question_type=q.question_type
        )
        
        parsed = resp.get("parsed_response", "A")
        is_correct = (parsed.strip().upper() == q.answer.strip().upper())
        if is_correct:
            correct_count += 1
            
        results.append({
            "id": q.id,
            "category": q.category,
            "subcategory": q.subcategory,
            "question": q.question,
            "options": q.options,
            "expected": q.answer,
            "predicted": parsed,
            "is_correct": is_correct,
            "raw_response": resp.get("raw_response", "")
        })
        
        if verbose and (i + 1) % 10 == 0:
            print(f"  [{i+1}/{len(target_questions)}] Current Accuracy: {correct_count/(i+1):.1%}")

    duration = time.time() - start_time
    accuracy = correct_count / len(target_questions) if target_questions else 0.0
    
    return {
        "suite": "cs_eval",
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": duration,
        "metrics": {
            "total": len(target_questions),
            "correct": correct_count,
            "accuracy": accuracy
        },
        "results": results
    }
