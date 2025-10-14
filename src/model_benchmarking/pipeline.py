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
    cybergym_config: Optional[Dict[str, Any]] = None,
    cvebench_config: Optional[Dict[str, Any]] = None,
) -> List[PipelineStepResult]:
    """Run the evaluation pipeline sequentially.

    Returns list of step results in execution order.
    """
    _maybe_setup_strands_telemetry(use_strands_telemetry)

    results: List[PipelineStepResult] = []

    # CS-Eval
    try:
        # Load cs-eval runner dynamically since folder name has a hyphen
        repo_root = Path(__file__).resolve().parents[2]
        cs_eval_path = repo_root / "benchmarking" / "cs-eval" / "run_evaluation.py"
        spec = importlib.util.spec_from_file_location("cs_eval_runner", str(cs_eval_path))
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to load CS-Eval runner module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        run_cs_eval_with_provider = getattr(module, "run_cs_eval_with_provider")

        cs = run_cs_eval_with_provider(
            provider,
            categories=categories,
            max_questions=max_questions,
            batch_size=10,
            output_dir=output_dir,
            verbose=verbose,
        )
        results.append(
            PipelineStepResult(
                name="cs-eval",
                status="ok",
                results_path=cs.get("results_path"),
                metrics=cs.get("metrics"),
            )
        )
    except Exception as e:
        results.append(PipelineStepResult(name="cs-eval", status=f"failed: {e}"))
        return results  # stop early if CS-Eval fails

    # CyberGym (placeholder for now)
    try:
        # Integrate CyberGym evaluation using provider
        repo_root = Path(__file__).resolve().parents[2]
        sample_file = str(repo_root / "benchmarking" / "cybergym" / "cybergym_subset_sample.json")
        # If sample file doesn't exist, attempt to use the one inside cybergym folder
        if not Path(sample_file).exists():
            sample_file = str(repo_root / "benchmarking" / "cybergym" / "cybergym" / "cybergym_subset_sample.json")

        # Dynamic import to avoid import path issues
        cybergym_eval_path = repo_root / "benchmarking" / "cybergym" / "evaluator.py"
        spec = importlib.util.spec_from_file_location("cybergym_evaluator", str(cybergym_eval_path))
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to load CyberGym evaluator module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        run_cybergym_with_provider = getattr(module, "run_cybergym_with_provider")

        cg = run_cybergym_with_provider(
            provider,
            sample_file=sample_file,
            output_dir=output_dir,
            max_items=max_questions,
            cybergym_config=locals().get("cybergym_config"),
        )
        results.append(
            PipelineStepResult(
                name="cybergym",
                status="ok",
                results_path=cg.get("results_path"),
                metrics=cg.get("metrics"),
            )
        )
    except Exception as e:
        results.append(PipelineStepResult(name="cybergym", status=f"failed: {e}"))

    # CVE-Bench (placeholder for now)
    try:
        # Integrate CVE-Bench placeholder evaluator
        repo_root = Path(__file__).resolve().parents[2]
        cve_eval_path = repo_root / "benchmarking" / "cve-bench" / "evaluator.py"
        spec = importlib.util.spec_from_file_location("cve_bench_evaluator", str(cve_eval_path))
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to load CVE-Bench evaluator module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        run_cve_bench = getattr(module, "run_cve_bench")

        cb = run_cve_bench(output_dir=output_dir)
        results.append(
            PipelineStepResult(
                name="cve-bench",
                status="ok",
                results_path=cb.get("results_path"),
                metrics=cb.get("metrics"),
            )
        )
    except Exception as e:
        results.append(PipelineStepResult(name="cve-bench", status=f"failed: {e}"))

    return results
