"""model_benchmarking package - thin wrappers and shared utilities."""

from .runner import run_benchmark
from .report import generate_report

__all__ = ["run_benchmark", "generate_report"]
