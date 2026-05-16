"""
Rubric-based graders using LLM-as-judge.

These graders send the submission to an LLM with a scoring rubric
and parse the response to get a score (0.0-1.0) and rationale.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models import GradeResult, Sample, ExtractorSpec
from .base import BaseGrader, GraderError


# Default system prompt for LLM judges
JUDGE_SYSTEM_PROMPT = """You are an evaluation judge. You will be given:
1. A rubric describing evaluation criteria
2. An input/question that was asked
3. A submission to evaluate

Evaluate the submission according to the rubric and return a JSON response with:
{
    "score": <a decimal number between 0.0 and 1.0>,
    "rationale": "<explanation of your grading decision>"
}

IMPORTANT:
- The score MUST be a number between 0.0 and 1.0 (inclusive)
- 0.0 means complete failure, 1.0 means perfect
- Use decimal values for partial credit (e.g., 0.25, 0.5, 0.75)
- Be objective and follow the rubric strictly
- Only return the JSON object, no other text"""


DEFAULT_RUBRIC = """Evaluate the quality and correctness of the response.

Scoring:
- 1.0: Excellent - Accurate, complete, well-structured
- 0.75: Good - Mostly correct with minor issues
- 0.5: Acceptable - Partially correct or incomplete
- 0.25: Poor - Significant errors or missing information
- 0.0: Incorrect - Wrong or completely irrelevant"""


class RubricGrader(BaseGrader):
    """
    Grader using an LLM as judge with a scoring rubric.
    
    Usage:
        grader = RubricGrader(
            prompt="Rate the helpfulness...",
            model="gpt-4o-mini",
        )
        result = grader.grade(sample, submission)
    """
    
    def __init__(
        self,
        prompt: Optional[str] = None,
        prompt_file: Optional[str] = None,
        model: str = "gpt-4o-mini",
        provider: Optional[str] = None,
        provider_host: Optional[str] = None,
        temperature: float = 0.0,
        extractor: Optional[ExtractorSpec] = None,
        rubric_vars: Optional[List[str]] = None,
        display_name: Optional[str] = None,
        base_dir: Optional[Path] = None,
    ):
        super().__init__(extractor=extractor, display_name=display_name)
        
        self.model = model
        self.provider_name = provider
        self.provider_host = provider_host
        self.temperature = temperature
        self.rubric_vars = rubric_vars or []
        self.base_dir = base_dir
        
        # Load rubric prompt
        if prompt:
            self.rubric = prompt
        elif prompt_file:
            prompt_path = Path(prompt_file)
            if not prompt_path.is_absolute() and base_dir:
                prompt_path = base_dir / prompt_path
            try:
                self.rubric = prompt_path.read_text(encoding="utf-8")
            except IOError as e:
                raise GraderError(f"Failed to load rubric file {prompt_path}: {e}")
        else:
            self.rubric = DEFAULT_RUBRIC
        
        # Lazy-loaded provider
        self._provider: Any = None
    
    def _get_provider(self) -> Any:
        """Get or create the judge provider."""
        if self._provider is not None:
            return self._provider
        
        from ...providers.factory import make_provider
        
        provider_name = self.provider_name or "ollama"
        host = self.provider_host or "http://localhost:11434"
        
        self._provider = make_provider(
            provider_name,
            model=self.model,
            host=host,
            temperature=self.temperature,
            max_tokens=512,
        )
        return self._provider
    
    def _build_prompt(self, sample: Sample, submission: str) -> str:
        """Build the judge prompt with rubric, input, and submission."""
        # Interpolate rubric variables
        rubric = self.rubric
        for var in self.rubric_vars:
            placeholder = "{{" + var + "}}"
            value = sample.rubric_vars.get(var, "")
            rubric = rubric.replace(placeholder, str(value))
        
        # Also support single-brace syntax
        for var in self.rubric_vars:
            placeholder = "{" + var + "}"
            value = sample.rubric_vars.get(var, "")
            rubric = rubric.replace(placeholder, str(value))
        
        prompt = f"""## Rubric
{rubric}

## Input/Question
{sample.input}

## Expected Answer (if provided)
{sample.ground_truth or "Not provided"}

## Submission to Evaluate
{submission}

## Your Evaluation (JSON format)
"""
        return prompt
    
    def _parse_response(self, response: str) -> GradeResult:
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
    
    def grade(
        self,
        sample: Sample,
        submission: str,
        **kwargs: Any,
    ) -> GradeResult:
        """Grade using the LLM judge."""
        # Validate rubric vars
        for var in self.rubric_vars:
            if var not in sample.rubric_vars:
                raise GraderError(
                    f"Sample missing required rubric variable: '{var}'"
                )
        
        provider = self._get_provider()
        prompt = self._build_prompt(sample, submission)
        
        try:
            # Use generate_text for general text generation
            response = provider.generate_text(prompt)
        except Exception as e:
            raise GraderError(f"Judge API call failed: {e}")
        
        return self._parse_response(response)


class AsyncRubricGrader(RubricGrader):
    """
    Async version of RubricGrader for use in async runners.
    
    Falls back to sync calls if the provider doesn't support async.
    """
    
    async def grade_async(
        self,
        sample: Sample,
        submission: str,
        **kwargs: Any,
    ) -> GradeResult:
        """Async grade using the LLM judge."""
        # Validate rubric vars
        for var in self.rubric_vars:
            if var not in sample.rubric_vars:
                raise GraderError(
                    f"Sample missing required rubric variable: '{var}'"
                )
        
        provider = self._get_provider()
        prompt = self._build_prompt(sample, submission)
        
        try:
            # Use generate_text_async for async generation
            response = await provider.generate_text_async(prompt)
        except Exception as e:
            raise GraderError(f"Judge API call failed: {e}")
        
        return self._parse_response(response)
