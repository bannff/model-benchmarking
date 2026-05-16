"""
Question parsing and filtering logic for CS-Eval.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class CSEvalQuestion:
    """Structured representation of a CS-Eval question."""
    id: str
    question: str
    options: List[str]
    answer: str
    category: str
    subcategory: str
    question_type: str = "multiple_choice"
    context: str = ""


def parse_questions(dataset: Any, verbose: bool = False) -> List[CSEvalQuestion]:
    """Parse raw dataset items into structured CSEvalQuestion objects."""
    questions = []
    for i, item in enumerate(dataset):
        try:
            # Standard CS-Eval format extraction
            options = [item.get(ch, '') for ch in ('A', 'B', 'C', 'D')]
            options = [opt for opt in options if str(opt).strip()]
            
            questions.append(CSEvalQuestion(
                id=f"cs_eval_{i}",
                question=item.get('question', ''),
                options=options,
                answer=item.get('answer', 'A'),
                category=item.get('category', 'Unknown'),
                subcategory=item.get('subcategory', 'Unknown'),
                question_type="multiple_choice" if len(options) > 2 else "true_false"
            ))
        except Exception as e:
            if verbose:
                print(f"⚠️ Error parsing question {i}: {e}")
            continue
    return questions


def filter_questions(
    questions: List[CSEvalQuestion],
    categories: Optional[List[str]] = None,
    max_per_category: Optional[int] = None
) -> List[CSEvalQuestion]:
    """Filter questions by category and count constraints."""
    filtered = questions
    
    if categories:
        filtered = [q for q in filtered if q.category in categories]
    
    if max_per_category:
        counts: Dict[str, int] = {}
        limited = []
        for q in filtered:
            if counts.get(q.category, 0) < max_per_category:
                limited.append(q)
                counts[q.category] = counts.get(q.category, 0) + 1
        filtered = limited
        
    return filtered
