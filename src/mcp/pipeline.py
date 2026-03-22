"""
Evaluation pipeline orchestrator.

Runs CS-Eval first, then CyberGym and CVE-Bench. Uses a provider interface
compatible with CS-Eval. Optionally uses Strands telemetry if available.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pathlib import Path
import importlib.util
import os

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


def _maybe_setup_strands_telemetry(enable: bool) -> None:
    if not enable:
        return
    try:  # pragma: no cover - env dependent
        from strands.telemetry import StrandsTelemetry  # type: ignore

        telemetry = StrandsTelemetry()  # type: ignore[call-arg, assignment]
        telemetry.setup_console_exporter()  # type: ignore[attr-defined]
        telemetry.setup_otlp_exporter()  # type: ignore[attr-defined]
        telemetry.setup_meter(enable_console_exporter=True, enable_otlp_exporter=True)  # type: ignore[attr-defined]
    except Exception:
        # Don't fail pipeline just because telemetry isn't configured
        pass


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
            # Use the adapter to keep logic encapsulated
            cs_adapter = CSEvalSuite()
            cs = cs_adapter.run(
                provider=provider,
                categories=categories,
                max_questions=max_questions,
                output_dir=output_dir,
                verbose=verbose,
                cs_eval_config=cs_eval_config,
            )
            results.append(
                PipelineStepResult(
                    name=cs.name,
                    status=cs.status,
                    results_path=cs.results_path,
                    metrics=cs.metrics,
                )
            )
        except Exception as e:
            results.append(PipelineStepResult(name="cs-eval", status=f"failed: {e}"))
            return results  # stop early if CS-Eval fails
    else:
        results.append(PipelineStepResult(name="cs-eval", status="skipped"))

    # CyberGym
    if skip_cybergym:
        results.append(PipelineStepResult(name="cybergym", status="skipped"))
    else:
        try:
            cg_adapter = CyberGymSuite()
            cg = cg_adapter.run(
                provider=provider,
                output_dir=output_dir,
                max_items=max_questions,
                cybergym_config=cybergym_config,
            )
            results.append(
                PipelineStepResult(
                    name=cg.name,
                    status=cg.status,
                    results_path=cg.results_path,
                    metrics=cg.metrics,
                )
            )
        except Exception as e:
            results.append(PipelineStepResult(name="cybergym", status=f"failed: {e}"))

    # CVE-Bench
    if skip_cvebench:
        results.append(PipelineStepResult(name="cve-bench", status="skipped"))
    else:
        try:
            cb_adapter = CVEBenchSuite()
            cb = cb_adapter.run(
                provider=provider,
                output_dir=output_dir,
                cvebench_config=cvebench_config,
            )
            results.append(
                PipelineStepResult(
                    name=cb.name,
                    status=cb.status,
                    results_path=cb.results_path,
                    metrics=cb.metrics,
                )
            )
        except Exception as e:
            results.append(PipelineStepResult(name="cve-bench", status=f"failed: {e}"))

    # Write manifest and index in output_dir capturing high-level pipeline run
    try:
        # Aggregate simple top-level metrics and artifacts
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
        # Write under output_dir (no per-run subdir yet to preserve current suite outputs)
        os.makedirs(output_dir, exist_ok=True)
        write_manifest(envelope, output_dir)
        append_index(envelope, output_dir)
    except Exception:
        # Never fail the pipeline return because manifest writing failed
        pass

    return results
