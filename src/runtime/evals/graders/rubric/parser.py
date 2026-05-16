"""
Parser for LLM judge responses.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict

from ...models import GradeResult
from ..base import GraderError

def parse_judge_response(response: str) -> GradeResult:
    """Parse the judge's response into a GradeResult."""
    response = response.strip()
    
    # Try to find JSON in the response
    json_match = re.search(r"\{[\s\S]*\}", response)
    if not json_match:
        # Fallback: try to extract score from text
        score_match = re.search(r"score[:\s]+(\d+\.?\d*)", response, re.IGNORECASE)
        if score_match:
            score = float(score_match.group(1))
            score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
            return GradeResult(score=score, rationale=response[:500])
        
        raise GraderError(f"Could not parse judge response: {response[:200]}")
    
    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        raise GraderError(f"Invalid JSON in judge response: {e}")
    
    score = data.get("score")
    if score is None:
        raise GraderError("Judge response missing 'score' field")
    
    try:
        score = float(score)
    except (TypeError, ValueError):
        raise GraderError(f"Invalid score value: {score}")
    
    # Clamp score to valid range
    score = max(0.0, min(1.0, score))
    
    rationale = data.get("rationale", "")
    
    return GradeResult(
        score=score,
        rationale=str(rationale)[:1000],
        metadata={"raw_response": response[:500]},
    )
