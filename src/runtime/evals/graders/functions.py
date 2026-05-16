"""
Grader functions for deterministic scoring.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from .base import normalize_text
from ..models import GradeResult


def exact_match(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """Check if submission exactly matches ground truth."""
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
    """Check if ground truth appears in submission."""
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
    """Check that ground truth does NOT appear in submission."""
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
    """Check if submission matches a regex pattern."""
    pattern = config.get("pattern", ground_truth)
    flags_str = config.get("flags", "")
    full_match = config.get("full_match", False)
    
    flags = 0
    if "i" in flags_str:
        flags |= re.IGNORECASE
    if "m" in flags_str:
        flags |= re.MULTILINE
    if "s" in flags_str:
        flags |= re.DOTALL
    
    try:
        import re as re_mod
        if full_match:
            match = re_mod.fullmatch(pattern, submission, flags)
        else:
            match = re_mod.search(pattern, submission, flags)
        
        if match:
            return GradeResult(score=1.0, rationale=f"Matched pattern: {pattern[:50]}")
        else:
            return GradeResult(score=0.0, rationale=f"Did not match pattern: {pattern[:50]}")
    except Exception as e:
        from .base import GraderError
        raise GraderError(f"Invalid regex pattern: {e}")


def starts_with(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """Check if submission starts with ground truth."""
    sub_norm = normalize_text(submission, config)
    gt_norm = normalize_text(ground_truth, config)
    if sub_norm.startswith(gt_norm):
        return GradeResult(score=1.0, rationale=f"Starts with '{ground_truth[:50]}'")
    return GradeResult(score=0.0, rationale=f"Does not start with '{ground_truth[:50]}'")


def ends_with(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """Check if submission ends with ground truth."""
    sub_norm = normalize_text(submission, config)
    gt_norm = normalize_text(ground_truth, config)
    if sub_norm.endswith(gt_norm):
        return GradeResult(score=1.0, rationale=f"Ends with '{ground_truth[:50]}'")
    return GradeResult(score=0.0, rationale=f"Does not end with '{ground_truth[:50]}'")


def numeric_match(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """Check if numeric values are equal within tolerance."""
    tolerance = config.get("tolerance", 1e-6)
    rel_tolerance = config.get("relative_tolerance", 1e-6)
    
    def extract_number(s: str) -> Optional[float]:
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
        return GradeResult(score=0.0, rationale="Could not extract numbers")
    
    abs_diff = abs(sub_num - gt_num)
    rel_diff = abs_diff / max(abs(gt_num), 1e-10)
    
    if abs_diff <= tolerance or rel_diff <= rel_tolerance:
        return GradeResult(score=1.0, rationale=f"Numeric match: {sub_num} ≈ {gt_num}")
    return GradeResult(score=0.0, rationale=f"Numeric mismatch: {sub_num} != {gt_num}")


def json_match(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """Check if JSON objects are structurally equal."""
    ignore_keys = set(config.get("ignore_keys", []))
    partial = config.get("partial", False)
    
    def parse_json(s: str) -> Any:
        s = s.strip()
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
        return GradeResult(score=0.0, rationale="Failed to parse JSON")
    
    sub_f = filter_keys(sub_json)
    gt_f = filter_keys(gt_json)
    
    if partial and isinstance(gt_f, dict) and isinstance(sub_f, dict):
        for k, v in gt_f.items():
            if k not in sub_f or sub_f[k] != v:
                return GradeResult(score=0.0, rationale=f"JSON mismatch at '{k}'")
        return GradeResult(score=1.0, rationale="Partial JSON match")
    
    if sub_f == gt_f:
        return GradeResult(score=1.0, rationale="JSON match")
    return GradeResult(score=0.0, rationale="JSON mismatch")


def length_check(submission: str, ground_truth: str, config: Dict[str, Any]) -> GradeResult:
    """Check if submission length is within range."""
    min_len = config.get("min_length", 1)
    max_len = config.get("max_length")
    unit = config.get("unit", "chars")
    
    length = len(submission.split()) if unit == "words" else len(submission)
    
    if length < min_len:
        return GradeResult(score=0.0, rationale=f"Too short: {length} < {min_len}")
    if max_len is not None and length > max_len:
        return GradeResult(score=0.0, rationale=f"Too long: {length} > {max_len}")
    
    return GradeResult(score=1.0, rationale=f"Length OK: {length}")
