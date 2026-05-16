"""
CVE-Bench suite adapter implementing the BaseSuite protocol.
Promoted to a native package in src/runtime/suites/cve_bench/.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from ..base import BaseSuite, SuiteOutcome
from .runner import run_cve_bench
from ...utils.reporting import save_suite_results


class CVEBenchSuite(BaseSuite):
    name = "cve-bench"

    async def run(
        self,
        *,
        provider: Any,
        output_dir: str,
        cvebench_config: Optional[Dict[str, Any]] = None,
        **_: Any,
    ) -> SuiteOutcome:
        """Run the CVE-Bench benchmark suite."""
        
        results = await run_cve_bench(
            provider=provider,
            output_dir=output_dir,
            cvebench_config=cvebench_config
        )
        
        res_path = save_suite_results(
            suite_name="cve_bench",
            output_dir=output_dir,
            results=results
        )
        
        return SuiteOutcome(
            name=self.name,
            status="ok",
            results_path=res_path,
            metrics=results.get("metrics"),
        )
