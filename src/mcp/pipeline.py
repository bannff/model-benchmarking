"""Compatibility wrapper for the public pipeline API.

Historically the public API exposed a synchronous `run_pipeline` helper even
though the underlying implementation is async. This module keeps that contract
stable while also exposing the native async function for modern callers.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from model_benchmarking_cli.pipeline import PipelineStepResult, run_pipeline as run_pipeline_async


def run_pipeline(
    *,
    provider: Any,
    categories: Optional[List[str]] = None,
    max_questions: Optional[int] = None,
    output_dir: str = "results",
    verbose: bool = False,
    use_strands_telemetry: bool = False,
    skip_cs_eval: bool = False,
    skip_cybergym: bool = False,
    skip_cvebench: bool = False,
    cs_eval_config: Optional[Dict[str, Any]] = None,
    cybergym_config: Optional[Dict[str, Any]] = None,
    cvebench_config: Optional[Dict[str, Any]] = None,
) -> List[PipelineStepResult]:
    """Run the async pipeline from synchronous callers."""

    return asyncio.run(
        run_pipeline_async(
            provider=provider,
            categories=categories,
            max_questions=max_questions,
            output_dir=output_dir,
            verbose=verbose,
            use_strands_telemetry=use_strands_telemetry,
            skip_cs_eval=skip_cs_eval,
            skip_cybergym=skip_cybergym,
            skip_cvebench=skip_cvebench,
            cs_eval_config=cs_eval_config,
            cybergym_config=cybergym_config,
            cvebench_config=cvebench_config,
        )
    )


__all__ = ["PipelineStepResult", "run_pipeline", "run_pipeline_async"]