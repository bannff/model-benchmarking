"""
Base grader interface and common utilities.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..models import GradeResult, Sample, ExtractorSpec
from ..extractors import get_extractor, BaseExtractor


class GraderError(Exception):
    """Error during grading."""
    pass


class BaseGrader(ABC):
    """
    Base class for graders.
    
    A grader takes a sample and submission (extracted from model response)
    and produces a GradeResult with a score (0.0-1.0) and optional rationale.
    """
    
    def __init__(
        self,
        extractor: Optional[ExtractorSpec] = None,
        display_name: Optional[str] = None,
    ):
        self.extractor_spec = extractor or ExtractorSpec(name="last_assistant")
        self.extractor: BaseExtractor = get_extractor(self.extractor_spec)
        self.display_name = display_name
    
    def extract(self, response: str, **kwargs: Any) -> str:
        """Extract submission from response using configured extractor."""
        return self.extractor.extract(response, **kwargs)
    
    @abstractmethod
    def grade(
        self,
        sample: Sample,
        submission: str,
        **kwargs: Any,
    ) -> GradeResult:
        """
        Grade a submission.
        
        Args:
            sample: The original sample with input/ground_truth
            submission: Extracted submission to grade
            **kwargs: Additional context
        
        Returns:
            GradeResult with score and rationale
        """
        pass
    
    def grade_response(
        self,
        sample: Sample,
        response: str,
        **kwargs: Any,
    ) -> GradeResult:
        """
        Convenience method: extract and grade in one step.
        
        Args:
            sample: The original sample
            response: Raw model response
            **kwargs: Additional context
        
        Returns:
            GradeResult with score and rationale
        """
        submission = self.extract(response, sample=sample, **kwargs)
        if not submission.strip():
            return GradeResult(
                score=0.0,
                rationale="Empty submission after extraction",
            )
        return self.grade(sample, submission, **kwargs)


def normalize_text(text: str, config: Optional[Dict[str, Any]] = None) -> str:
    """
    Normalize text for comparison.
    
    Config options:
        case_sensitive: If False (default), convert to lowercase
        strip_whitespace: If True (default), strip leading/trailing whitespace
        strip_punctuation: If True, remove punctuation
        collapse_whitespace: If True, collapse multiple whitespace to single space
    """
    config = config or {}
    
    text = text or ""
    
    if config.get("strip_whitespace", True):
        text = text.strip()
    
    if not config.get("case_sensitive", False):
        text = text.lower()
    
    if config.get("collapse_whitespace", False):
        import re
        text = re.sub(r"\s+", " ", text)
    
    if config.get("strip_punctuation", False):
        import string
        text = text.translate(str.maketrans("", "", string.punctuation))
    
    return text
