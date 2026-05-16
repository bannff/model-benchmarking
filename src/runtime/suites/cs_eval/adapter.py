"""
CS-Eval suite adapter implementing the BaseSuite protocol.
Now promoted to a native package in src/runtime/suites/cs_eval/.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from ..base import BaseSuite, SuiteOutcome
from .runner import run_cs_eval
from ...utils.reporting import save_suite_results


class CSEvalSuite(BaseSuite):
    name = "cs-eval"

    async def run(
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
        """Run the CS-Eval benchmark suite."""
        
        # Default to local sample in data/ if no config provided
        local_sample = (cs_eval_config or {}).get("local_sample_path")
        if not local_sample:
            local_sample = str(Path(__file__).parent / "data" / "sample_questions.jsonl")
        
        results = await run_cs_eval(
            provider=provider,
            categories=categories,
            max_questions=max_questions,
            local_sample=local_sample,
            verbose=verbose
        )
        
        # Save results using the central reporting utility
        res_path = save_suite_results(
            suite_name="cs_eval",
            output_dir=output_dir,
            results=results
        )
        
        return SuiteOutcome(
            name=self.name,
            status="ok",
            results_path=res_path,
            metrics=results.get("metrics"),
        )
