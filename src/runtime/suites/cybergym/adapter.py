"""
CyberGym suite adapter implementing the BaseSuite protocol.
Promoted to a native package in src/runtime/suites/cybergym/.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from ..base import BaseSuite, SuiteOutcome
from .runner import run_cybergym
from ...utils.reporting import save_suite_results


class CyberGymSuite(BaseSuite):
    name = "cybergym"

    async def run(
        self,
        *,
        provider: Any,
        output_dir: str,
        max_items: Optional[int] = None,
        cybergym_config: Optional[Dict[str, Any]] = None,
        **_: Any,
    ) -> SuiteOutcome:
        """Run the CyberGym benchmark suite."""
        
        # Resolve sample file path from the new package-relative data directory
        sample_file = Path(__file__).parent / "data" / "cybergym_subset_sample.json"
             
        results = await run_cybergym(
            provider=provider,
            sample_file=str(sample_file),
            output_dir=output_dir,
            max_items=max_items,
            cybergym_config=cybergym_config
        )
        
        res_path = save_suite_results(
            suite_name="cybergym",
            output_dir=output_dir,
            results=results
        )
        
        return SuiteOutcome(
            name=self.name,
            status="ok",
            results_path=res_path,
            metrics=results.get("metrics"),
        )
