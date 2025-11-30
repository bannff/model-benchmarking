"""
Evals Framework - A modular, provider-agnostic evaluation system.

Inspired by Letta Evals, this framework provides:
- JSONL dataset loading with metadata support
- Pluggable extractors for parsing model responses
- Tool graders (exact_match, contains, regex) and LLM-as-judge rubric graders
- Configurable pass/fail gates
- YAML-driven suite definitions
- Async runner with concurrent execution

Usage:
    from model_benchmarking.evals import run_suite, EvalRunner
    
    # Run from YAML config
    result = await run_suite("suite.yaml", provider)
    
    # Or programmatically
    runner = EvalRunner(suite_spec, provider)
    result = await runner.run()
"""

from .models import (
    Sample,
    GradeResult,
    SampleResult,
    Metrics,
    RunnerResult,
    GraderSpec,
    ExtractorSpec,
    GateSpec,
    TargetSpec,
    SuiteSpec,
)
from .dataset import load_dataset, DatasetError
from .extractors import get_extractor, ExtractorRegistry
from .graders import get_grader, GraderRegistry, ToolGrader, RubricGrader
from .gates import check_gate, GateEvaluator
from .suite import load_suite, SuiteLoader
from .runner import EvalRunner, run_suite

__all__ = [
    # Models
    "Sample",
    "GradeResult",
    "SampleResult",
    "Metrics",
    "RunnerResult",
    "GraderSpec",
    "ExtractorSpec",
    "GateSpec",
    "TargetSpec",
    "SuiteSpec",
    # Dataset
    "load_dataset",
    "DatasetError",
    # Extractors
    "get_extractor",
    "ExtractorRegistry",
    # Graders
    "get_grader",
    "GraderRegistry",
    "ToolGrader",
    "RubricGrader",
    # Gates
    "check_gate",
    "GateEvaluator",
    # Suite
    "load_suite",
    "SuiteLoader",
    # Runner
    "EvalRunner",
    "run_suite",
]
