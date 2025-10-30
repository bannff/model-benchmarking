"""
CS-Eval suite adapter implementing the BaseSuite protocol.
"""
from __future__ import annotations

from pathlib import Path
import importlib.util
from typing import Any, Dict, Optional

from .base import BaseSuite, SuiteOutcome


class CSEvalSuite(BaseSuite):
    name = "cs-eval"

    def run(
        self,
        *,
        provider: Any,
        output_dir: str,
        categories: Optional[list[str]] = None,
        max_questions: Optional[int] = None,
        verbose: bool = False,
        cs_eval_config: Optional[Dict[str, Any]] = None,
        **_: Any,
    ) -> SuiteOutcome:
        # Load cs-eval runner dynamically since folder name has a hyphen
        repo_root = Path(__file__).resolve().parents[3]
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
            # pass through local sample path if provided
            local_sample_path=(cs_eval_config or {}).get("local_sample_path"),
        )
        return SuiteOutcome(
            name=self.name,
            status="ok",
            results_path=cs.get("results_path"),
            metrics=cs.get("metrics"),
        )
