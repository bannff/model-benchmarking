"""Public compatibility package for the benchmark API."""

from .cli import main, start
from .pipeline import run_pipeline, run_pipeline_async
from .report import generate_report
from .runner import BenchmarkResult, run_benchmark

__all__ = [
    "BenchmarkResult",
    "generate_report",
    "main",
    "run_benchmark",
    "run_pipeline",
    "run_pipeline_async",
    "start",
]