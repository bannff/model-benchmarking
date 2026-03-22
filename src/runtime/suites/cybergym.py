"""
CyberGym suite adapter implementing the BaseSuite protocol.
"""
from __future__ import annotations

from pathlib import Path
import importlib.util
from typing import Any, Dict, Optional

from .base import BaseSuite, SuiteOutcome


class CyberGymSuite(BaseSuite):
    name = "cybergym"

    def run(
        self,
        *,
        provider: Any,
        output_dir: str,
        max_items: Optional[int] = None,
        cybergym_config: Optional[Dict[str, Any]] = None,
        **_: Any,
    ) -> SuiteOutcome:
        # Dynamic import to avoid sys.path issues
        repo_root = Path(__file__).resolve().parents[3]
        cybergym_eval_path = repo_root / "benchmarking" / "cybergym" / "evaluator.py"
        spec = importlib.util.spec_from_file_location("cybergym_evaluator", str(cybergym_eval_path))
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to load CyberGym evaluator module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        run_cybergym_with_provider = getattr(module, "run_cybergym_with_provider")

        # Resolve sample file
        sample_file = str(repo_root / "benchmarking" / "cybergym" / "cybergym_subset_sample.json")
        if not Path(sample_file).exists():
            sample_file = str(repo_root / "benchmarking" / "cybergym" / "cybergym" / "cybergym_subset_sample.json")

        res = run_cybergym_with_provider(
            provider,
            sample_file=sample_file,
            output_dir=output_dir,
            max_items=max_items,
            cybergym_config=cybergym_config,
        )
        return SuiteOutcome(
            name=self.name,
            status="ok",
            results_path=res.get("results_path"),
            metrics=res.get("metrics"),
        )
