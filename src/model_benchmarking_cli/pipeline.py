"""
Evaluation pipeline orchestrator.

Runs CS-Eval first, then CyberGym and CVE-Bench. Uses a provider interface
compatible with CS-Eval. Optionally uses Strands telemetry if available.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import os
import warnings

from runtime.utils.result_schema import ResultEnvelope, write_manifest, append_index, iso_now
from runtime.suites.cs_eval import CSEvalSuite
from runtime.suites.cybergym import CyberGymSuite
from runtime.suites.cve_bench import CVEBenchSuite
from runtime.utils.run_metadata import new_run_id, collect_environment_snapshot


@dataclass
class PipelineStepResult:
    name: str
    status: str
    results_path: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


def _step_from_outcome(outcome: Any) -> PipelineStepResult:
    return PipelineStepResult(
        name=outcome.name,
        status=outcome.status,
        results_path=outcome.results_path,
        metrics=outcome.metrics,
    )


async def _run_step(adapter: Any, **kwargs: Any) -> PipelineStepResult:
    outcome = await adapter.run(**kwargs)
    return _step_from_outcome(outcome)


def _append_failure(results: List[PipelineStepResult], name: str, exc: Exception) -> None:
    results.append(PipelineStepResult(name=name, status=f"failed: {exc}"))


def _write_pipeline_artifacts(
    *,
    provider: Any,
    output_dir: str,
    run_id: str,
    started_at: str,
    env_snapshot: Dict[str, Any],
    results: List[PipelineStepResult],
) -> None:
    overall_status = "ok" if all(r.status == "ok" or r.status == "skipped" for r in results) else "failed"
    artifacts: Dict[str, Any] = {
        "steps": [
            {
                "name": r.name,
                "status": r.status,
                "results_path": r.results_path,
                "metrics": r.metrics,
            }
            for r in results
        ],
        "env": env_snapshot,
    }
    envelope = ResultEnvelope(
        run_id=run_id,
        suite="pipeline",
        model=str(getattr(provider, "model", "unknown")),
        provider=provider.__class__.__name__,
        started_at=started_at,
        finished_at=iso_now(),
        status=overall_status,
        metrics={
            "steps_ok": sum(1 for r in results if r.status == "ok"),
            "steps_skipped": sum(1 for r in results if r.status == "skipped"),
            "steps_failed": sum(1 for r in results if r.status not in ("ok", "skipped")),
        },
        artifacts=artifacts,
    )
    os.makedirs(output_dir, exist_ok=True)
    write_manifest(envelope, output_dir)
    append_index(envelope, output_dir)


def _maybe_setup_strands_telemetry(enable: bool) -> None:
    if not enable:
        return
    try:  # pragma: no cover - env dependent
        from strands.telemetry import StrandsTelemetry  # type: ignore

        telemetry = StrandsTelemetry()  # type: ignore[call-arg, assignment]
        telemetry.setup_console_exporter()  # type: ignore[attr-defined]
        telemetry.setup_otlp_exporter()  # type: ignore[attr-defined]
        telemetry.setup_meter(enable_console_exporter=True, enable_otlp_exporter=True)  # type: ignore[attr-defined]
    except Exception as exc:
        warnings.warn(f"Strands telemetry disabled: {exc}", RuntimeWarning, stacklevel=2)


async def run_pipeline(
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
    """Run the evaluation pipeline sequentially.

    Returns list of step results in execution order.
    """
    _maybe_setup_strands_telemetry(use_strands_telemetry)

    results: List[PipelineStepResult] = []

    # Initialize run context
    run_id = new_run_id("pipeline")
    started_at = iso_now()
    env_snapshot = collect_environment_snapshot()

    # CS-Eval
    if not skip_cs_eval:
        try:
            cs = await _run_step(
                CSEvalSuite(),
                provider=provider,
                categories=categories,
                max_questions=max_questions,
                output_dir=output_dir,
                verbose=verbose,
                cs_eval_config=cs_eval_config,
            )
            results.append(cs)
        except Exception as e:
            _append_failure(results, "cs-eval", e)
            return results  # stop early if CS-Eval fails
    else:
        results.append(PipelineStepResult(name="cs-eval", status="skipped"))

    # CyberGym
    if skip_cybergym:
        results.append(PipelineStepResult(name="cybergym", status="skipped"))
    else:
        try:
            cg = await _run_step(
                CyberGymSuite(),
                provider=provider,
                output_dir=output_dir,
                max_items=max_questions,
                cybergym_config=cybergym_config,
            )
            results.append(cg)
        except Exception as e:
            _append_failure(results, "cybergym", e)

    # CVE-Bench
    if skip_cvebench:
        results.append(PipelineStepResult(name="cve-bench", status="skipped"))
    else:
        try:
            cb = await _run_step(
                CVEBenchSuite(),
                provider=provider,
                output_dir=output_dir,
                cvebench_config=cvebench_config,
            )
            results.append(cb)
        except Exception as e:
            _append_failure(results, "cve-bench", e)

    try:
        _write_pipeline_artifacts(
            provider=provider,
            output_dir=output_dir,
            run_id=run_id,
            started_at=started_at,
            env_snapshot=env_snapshot,
            results=results,
        )
    except Exception as exc:
        warnings.warn(f"Pipeline manifest write skipped: {exc}", RuntimeWarning, stacklevel=2)

    return results
