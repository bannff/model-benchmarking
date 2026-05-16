"""
Core evaluation runner implementation.
"""
from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..models import (
    SuiteSpec,
    Sample,
    GradeResult,
    SampleResult,
    RunnerResult,
)
from ..dataset import load_dataset_list
from ..graders import get_grader, BaseGrader
from ..gates import GateEvaluator, calculate_metrics


class EvalRunner:
    """Main evaluation runner."""
    
    def __init__(self, suite: SuiteSpec, provider: Any, verbose: bool = False):
        self.suite = suite
        self.provider = provider
        self.verbose = verbose
        self.graders: Dict[str, BaseGrader] = {
            name: get_grader(spec, base_dir=suite.base_dir)
            for name, spec in suite.graders.items()
        }
        self.gate_evaluator = GateEvaluator(suite.gate)
        self.results: List[SampleResult] = []
    
    def _log(self, message: str) -> None:
        if self.verbose: print(f"[EvalRunner] {message}")
    
    async def _run_sample(self, sample: Sample) -> SampleResult:
        start_time = time.time()
        model_name = getattr(self.provider, "model", "unknown")
        try:
            prompt = f"{sample.context}\n\n{sample.input}" if sample.context else sample.input
            # Use the new async provider interface
            response = await self.provider.generate_text(prompt)
            latency_ms = (time.time() - start_time) * 1000
            
            grades: Dict[str, GradeResult] = {}
            primary_grade: Optional[GradeResult] = None
            primary_submission: str = ""
            
            for name, grader in self.graders.items():
                submission = grader.extract(response, sample=sample)
                grade = await grader.grade(sample, submission)
                grades[name] = grade
                if primary_grade is None:
                    primary_grade = grade
                    primary_submission = submission
            
            if primary_grade is None:
                primary_grade = GradeResult(score=0.0, rationale="No graders")
                primary_submission = response
            
            return SampleResult(
                sample=sample, response=response, submission=primary_submission,
                grade=primary_grade, grades=grades if len(grades) > 1 else None,
                model_name=model_name, latency_ms=latency_ms, error=None,
            )
        except Exception as e:
            return SampleResult(
                sample=sample, response="", submission="",
                grade=GradeResult(score=0.0, rationale=f"Error: {str(e)[:100]}"),
                grades=None, model_name=model_name, latency_ms=(time.time() - start_time) * 1000,
                error=str(e),
            )

    async def run(self, samples: Optional[List[Sample]] = None) -> RunnerResult:
        """
        Run the evaluation.
        
        Args:
            samples: Optional list of pre-loaded samples. If not provided,
                     samples will be loaded from the suite's dataset path.
        """
        started_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        
        if samples is None:
            samples = load_dataset_list(
                self.suite.dataset,
                max_samples=self.suite.max_samples,
                sample_tags=self.suite.sample_tags,
                base_dir=self.suite.base_dir
            )
            
        self._log(f"Loaded {len(samples)} samples")
        
        semaphore = asyncio.Semaphore(self.suite.max_concurrent)
        async def run_with_semaphore(s: Sample) -> SampleResult:
            async with semaphore: return await self._run_sample(s)
        
        tasks = [run_with_semaphore(s) for s in samples]
        self.results = []
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            self.results.append(await coro)
            if self.verbose and (i + 1) % 10 == 0: self._log(f"Progress: {i + 1}/{len(samples)}")
        
        finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        metrics = calculate_metrics(self.results, list(self.graders.keys()))
        gate_passed, gate_details = self.gate_evaluator.evaluate(self.results)
        
        return RunnerResult(
            suite_name=self.suite.name, model_name=getattr(self.provider, "model", "unknown"),
            provider_name=self.provider.__class__.__name__, started_at=started_at, finished_at=finished_at,
            results=self.results, metrics=metrics, gate_passed=gate_passed, gate_details=gate_details,
            config={"suite": self.suite.name, "dataset": str(self.suite.dataset), "max_samples": self.suite.max_samples}
        )
