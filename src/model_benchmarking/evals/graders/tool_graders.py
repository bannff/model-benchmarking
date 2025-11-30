"""
Tool-based graders for fast, deterministic scoring.

Built-in functions:
- exact_match: Exact string equality (after normalization)
- contains: Ground truth is substring of submission
- regex: Submission matches a regex pattern
- starts_with: Submission starts with ground truth
- ends_with: Submission ends with ground truth
- numeric_match: Numbers are equal (within tolerance)
- json_match: JSON objects are structurally equal
"""
from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict, Optional

from ..models import GradeResult, Sample, ExtractorSpec
from .base import BaseGrader, GraderError, normalize_text


# Type for grader functions
GraderFunction = Callable[[str, str, Dict[str, Any]], GradeResult]


def exact_match(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """
    Check if submission exactly matches ground truth.
    
    Config:
        case_sensitive: If True, comparison is case-sensitive (default: False)
        strip_whitespace: If True, strip whitespace before comparison (default: True)
    """
    sub_norm = normalize_text(submission, config)
    gt_norm = normalize_text(ground_truth, config)
    
    if sub_norm == gt_norm:
        return GradeResult(score=1.0, rationale="Exact match")
    else:
        return GradeResult(
            score=0.0,
            rationale=f"No match: expected '{gt_norm[:100]}', got '{sub_norm[:100]}'"
        )


def contains(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """
    Check if ground truth appears in submission.
    
    Config:
        case_sensitive: If True, comparison is case-sensitive (default: False)
    """
    sub_norm = normalize_text(submission, config)
    gt_norm = normalize_text(ground_truth, config)
    
    if gt_norm in sub_norm:
        return GradeResult(score=1.0, rationale=f"Contains '{ground_truth[:50]}'")
    else:
        return GradeResult(
            score=0.0,
            rationale=f"Does not contain '{ground_truth[:50]}'"
        )


def not_contains(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """
    Check that ground truth does NOT appear in submission.
    Useful for checking model doesn't include forbidden content.
    """
    sub_norm = normalize_text(submission, config)
    gt_norm = normalize_text(ground_truth, config)
    
    if gt_norm not in sub_norm:
        return GradeResult(score=1.0, rationale=f"Correctly does not contain '{ground_truth[:50]}'")
    else:
        return GradeResult(
            score=0.0,
            rationale=f"Incorrectly contains '{ground_truth[:50]}'"
        )


def regex_match(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """
    Check if submission matches a regex pattern.
    
    The pattern is taken from ground_truth, or can be overridden in config.
    
    Config:
        pattern: Regex pattern (overrides ground_truth)
        flags: Regex flags string ("i" for case-insensitive, "m" for multiline, "s" for dotall)
        full_match: If True, pattern must match entire string (default: False)
    """
    pattern = config.get("pattern", ground_truth)
    flags_str = config.get("flags", "")
    full_match = config.get("full_match", False)
    
    # Parse flags
    flags = 0
    if "i" in flags_str:
        flags |= re.IGNORECASE
    if "m" in flags_str:
        flags |= re.MULTILINE
    if "s" in flags_str:
        flags |= re.DOTALL
    
    try:
        if full_match:
            match = re.fullmatch(pattern, submission, flags)
        else:
            match = re.search(pattern, submission, flags)
        
        if match:
            return GradeResult(
                score=1.0,
                rationale=f"Matched pattern: {pattern[:50]}"
            )
        else:
            return GradeResult(
                score=0.0,
                rationale=f"Did not match pattern: {pattern[:50]}"
            )
    except re.error as e:
        raise GraderError(f"Invalid regex pattern: {e}")


def starts_with(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """Check if submission starts with ground truth."""
    sub_norm = normalize_text(submission, config)
    gt_norm = normalize_text(ground_truth, config)
    
    if sub_norm.startswith(gt_norm):
        return GradeResult(score=1.0, rationale=f"Starts with '{ground_truth[:50]}'")
    else:
        return GradeResult(score=0.0, rationale=f"Does not start with '{ground_truth[:50]}'")


def ends_with(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """Check if submission ends with ground truth."""
    sub_norm = normalize_text(submission, config)
    gt_norm = normalize_text(ground_truth, config)
    
    if sub_norm.endswith(gt_norm):
        return GradeResult(score=1.0, rationale=f"Ends with '{ground_truth[:50]}'")
    else:
        return GradeResult(score=0.0, rationale=f"Does not end with '{ground_truth[:50]}'")


def numeric_match(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """
    Check if numeric values are equal within tolerance.
    
    Config:
        tolerance: Absolute tolerance (default: 1e-6)
        relative_tolerance: Relative tolerance (default: 1e-6)
    """
    tolerance = config.get("tolerance", 1e-6)
    rel_tolerance = config.get("relative_tolerance", 1e-6)
    
    # Extract numbers from strings
    def extract_number(s: str) -> Optional[float]:
        # Try to find a number in the string
        match = re.search(r"-?\d+\.?\d*(?:e[+-]?\d+)?", s, re.IGNORECASE)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None
    
    sub_num = extract_number(submission)
    gt_num = extract_number(ground_truth)
    
    if sub_num is None or gt_num is None:
        return GradeResult(
            score=0.0,
            rationale=f"Could not extract numbers: submission='{submission[:50]}', expected='{ground_truth[:50]}'"
        )
    
    # Check absolute and relative tolerance
    abs_diff = abs(sub_num - gt_num)
    rel_diff = abs_diff / max(abs(gt_num), 1e-10)
    
    if abs_diff <= tolerance or rel_diff <= rel_tolerance:
        return GradeResult(
            score=1.0,
            rationale=f"Numeric match: {sub_num} ≈ {gt_num}"
        )
    else:
        return GradeResult(
            score=0.0,
            rationale=f"Numeric mismatch: {sub_num} != {gt_num} (diff={abs_diff})"
        )


def json_match(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """
    Check if JSON objects are structurally equal.
    
    Config:
        ignore_keys: List of keys to ignore in comparison
        partial: If True, only check keys present in ground_truth (default: False)
    """
    ignore_keys = set(config.get("ignore_keys", []))
    partial = config.get("partial", False)
    
    def parse_json(s: str) -> Any:
        s = s.strip()
        # Handle markdown code blocks
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", s)
        if match:
            s = match.group(1).strip()
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return None
    
    def filter_keys(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: filter_keys(v) for k, v in obj.items() if k not in ignore_keys}
        elif isinstance(obj, list):
            return [filter_keys(item) for item in obj]
        return obj
    
    sub_json = parse_json(submission)
    gt_json = parse_json(ground_truth)
    
    if sub_json is None or gt_json is None:
        return GradeResult(
            score=0.0,
            rationale="Failed to parse JSON"
        )
    
    sub_filtered = filter_keys(sub_json)
    gt_filtered = filter_keys(gt_json)
    
    if partial and isinstance(gt_filtered, dict) and isinstance(sub_filtered, dict):
        # Only check keys present in ground truth
        for key, value in gt_filtered.items():
            if key not in sub_filtered or sub_filtered[key] != value:
                return GradeResult(
                    score=0.0,
                    rationale=f"JSON mismatch at key '{key}'"
                )
        return GradeResult(score=1.0, rationale="Partial JSON match")
    
    if sub_filtered == gt_filtered:
        return GradeResult(score=1.0, rationale="JSON match")
    else:
        return GradeResult(score=0.0, rationale="JSON mismatch")


def length_check(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """
    Check if submission length is within expected range.
    
    Config:
        min_length: Minimum length (default: 1)
        max_length: Maximum length (optional)
        unit: "chars" or "words" (default: "chars")
    """
    min_len = config.get("min_length", 1)
    max_len = config.get("max_length")
    unit = config.get("unit", "chars")
    
    if unit == "words":
        length = len(submission.split())
    else:
        length = len(submission)
    
    if length < min_len:
        return GradeResult(
            score=0.0,
            rationale=f"Too short: {length} {unit} < {min_len}"
        )
    
    if max_len is not None and length > max_len:
        return GradeResult(
            score=0.0,
            rationale=f"Too long: {length} {unit} > {max_len}"
        )
    
    return GradeResult(
        score=1.0,
        rationale=f"Length OK: {length} {unit}"
    )


# Registry of built-in grader functions
TOOL_GRADER_FUNCTIONS: Dict[str, GraderFunction] = {
    "exact_match": exact_match,
    "exact": exact_match,
    "contains": contains,
    "includes": contains,
    "not_contains": not_contains,
    "excludes": not_contains,
    "regex": regex_match,
    "regex_match": regex_match,
    "starts_with": starts_with,
    "ends_with": ends_with,
    "numeric": numeric_match,
    "numeric_match": numeric_match,
    "json": json_match,
    "json_match": json_match,
    "length": length_check,
    "length_check": length_check,
}


class ToolGrader(BaseGrader):
    """
    Grader using deterministic tool functions.
    
    Usage:
        grader = ToolGrader(function="contains")
        result = grader.grade(sample, submission)
    """
    
    def __init__(
        self,
        function: str,
        extractor: Optional[ExtractorSpec] = None,
        config: Optional[Dict[str, Any]] = None,
        display_name: Optional[str] = None,
    ):
        super().__init__(extractor=extractor, display_name=display_name)
        
        if function not in TOOL_GRADER_FUNCTIONS:
            available = ", ".join(sorted(TOOL_GRADER_FUNCTIONS.keys()))
            raise GraderError(
                f"Unknown grader function: '{function}'. Available: {available}"
            )
        
        self.function_name = function
        self.grader_func = TOOL_GRADER_FUNCTIONS[function]
        self.config = config or {}
    
    def grade(
        self,
        sample: Sample,
        submission: str,
        **kwargs: Any,
    ) -> GradeResult:
        """Grade using the configured tool function."""
        ground_truth = sample.ground_truth
        
        if ground_truth is None:
            raise GraderError(
                f"Tool grader '{self.function_name}' requires ground_truth in sample"
            )
        
        return self.grader_func(submission, ground_truth, self.config)
