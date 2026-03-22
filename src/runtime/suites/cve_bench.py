"""
CVE-Bench suite adapter implementing the BaseSuite protocol.
"""
from __future__ import annotations

from pathlib import Path
import importlib.util
from typing import Any, Dict, Optional

from .base import BaseSuite, SuiteOutcome


class CVEBenchSuite(BaseSuite):
    name = "cve-bench"

    def run(
        self,
        *,
        provider: Any,
        output_dir: str,
        cvebench_config: Optional[Dict[str, Any]] = None,
        **_: Any,
    ) -> SuiteOutcome:
        # Dynamic import to avoid sys.path issues
        repo_root = Path(__file__).resolve().parents[3]
        cve_eval_path = repo_root / "benchmarking" / "cve-bench" / "evaluator.py"
        spec = importlib.util.spec_from_file_location("cve_bench_evaluator", str(cve_eval_path))
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to load CVE-Bench evaluator module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        run_cve_bench = getattr(module, "run_cve_bench")

        res = run_cve_bench(output_dir=output_dir, cvebench_config=cvebench_config, provider=provider)
        return SuiteOutcome(
            name=self.name,
            status="ok",
            results_path=res.get("results_path"),
            metrics=res.get("metrics"),
        )
