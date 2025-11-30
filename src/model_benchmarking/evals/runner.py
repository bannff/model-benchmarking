"""
Evaluation runner - orchestrates the full evaluation pipeline.

Flow:
    Dataset → Target (Model) → Extractor → Grader → Gate → Result
"""
from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .models import (
    SuiteSpec,
    Sample,
    GradeResult,
    SampleResult,
    Metrics,
    RunnerResult,
    GraderSpec,
)
from .dataset import load_dataset_list
from .graders import get_grader, BaseGrader
from .gates import GateEvaluator, calculate_metrics
from .suite import load_suite


class EvalRunner:
    """
    Main evaluation runner.
    
    Orchestrates:
    1. Loading samples from dataset
    2. Running each sample through the target model
    3. Extracting and grading responses
    4. Aggregating metrics
    5. Checking pass/fail gates
    
    Usage:
        runner = EvalRunner(suite, provider)
        result = await runner.run()
    """
    
    def __init__(
        self,
        suite: SuiteSpec,
        provider: Any,
        verbose: bool = False,
    ):
        self.suite = suite
        self.provider = provider
        self.verbose = verbose
        
        # Initialize graders
        self.graders: Dict[str, BaseGrader] = {}
        for name, spec in suite.graders.items():
            self.graders[name] = get_grader(spec, base_dir=suite.base_dir)
        
        # Gate evaluator
        self.gate_evaluator = GateEvaluator(suite.gate)
        
        # Results storage
        self.results: List[SampleResult] = []
    
    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[EvalRunner] {message}")
    
    async def _run_sample(self, sample: Sample) -> SampleResult:
        """
        Run a single sample through the evaluation pipeline.
        
        1. Send input to model
        2. Extract submission from response
        3. Grade with each configured grader
        """
        start_time = time.time()
        model_name = getattr(self.provider, "model", "unknown")
        
        try:
            # Build prompt
            prompt = sample.input
            if sample.context:
                prompt = f"{sample.context}\n\n{prompt}"
            
            # Get model response
            # Try async first, fall back to sync
            if hasattr(self.provider, "generate_text_async") and callable(getattr(self.provider, "generate_text_async", None)):
                response = await self.provider.generate_text_async(prompt)
            else:
                # Run sync method in executor to avoid blocking
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    self.provider.generate_text,
                    prompt,
                )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Grade with each grader
            grades: Dict[str, GradeResult] = {}
            primary_grade: Optional[GradeResult] = None
            primary_submission: str = ""
            
            for name, grader in self.graders.items():
                # Extract submission using grader's extractor
                submission = grader.extract(response, sample=sample)
                grade = grader.grade(sample, submission)
                grades[name] = grade
                
                # First grader is primary
                if primary_grade is None:
                    primary_grade = grade
                    primary_submission = submission
            
            # Ensure we have a primary grade
            if primary_grade is None:
                primary_grade = GradeResult(score=0.0, rationale="No graders configured")
                primary_submission = response
            
            return SampleResult(
                sample=sample,
                response=response,
                submission=primary_submission,
                grade=primary_grade,
                grades=grades if len(grades) > 1 else None,
                model_name=model_name,
                latency_ms=latency_ms,
                error=None,
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._log(f"Error on sample {sample.id}: {e}")
            
            return SampleResult(
                sample=sample,
                response="",
                submission="",
                grade=GradeResult(score=0.0, rationale=f"Error: {str(e)[:200]}"),
                grades=None,
                model_name=model_name,
                latency_ms=latency_ms,
                error=str(e),
            )
    
    async def run(self) -> RunnerResult:
        """
        Run the full evaluation pipeline.
        
        Returns:
            RunnerResult with all sample results and aggregate metrics
        """
        started_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        
        # Load samples
        self._log(f"Loading dataset: {self.suite.dataset}")
        samples = load_dataset_list(
            self.suite.dataset,
            max_samples=self.suite.max_samples,
            sample_tags=self.suite.sample_tags,
            base_dir=self.suite.base_dir,
        )
        self._log(f"Loaded {len(samples)} samples")
        
        # Run samples with concurrency control
        semaphore = asyncio.Semaphore(self.suite.max_concurrent)
        
        async def run_with_semaphore(sample: Sample) -> SampleResult:
            async with semaphore:
                return await self._run_sample(sample)
        
        # Create tasks
        tasks = [run_with_semaphore(sample) for sample in samples]
        
        # Run with progress logging
        self.results = []
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            self.results.append(result)
            
            if self.verbose and (i + 1) % 10 == 0:
                self._log(f"Progress: {i + 1}/{len(samples)}")
        
        finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        
        # Calculate metrics
        grader_keys = list(self.graders.keys())
        metrics = calculate_metrics(self.results, grader_keys)
        
        # Check gate
        gate_passed, gate_details = self.gate_evaluator.evaluate(self.results)
        
        self._log(f"Evaluation complete: {gate_details}")
        
        # Build result
        return RunnerResult(
            suite_name=self.suite.name,
            model_name=getattr(self.provider, "model", "unknown"),
            provider_name=self.provider.__class__.__name__,
            started_at=started_at,
            finished_at=finished_at,
            results=self.results,
            metrics=metrics,
            gate_passed=gate_passed,
            gate_details=gate_details,
            config={
                "suite": self.suite.name,
                "dataset": str(self.suite.dataset),
                "max_samples": self.suite.max_samples,
                "max_concurrent": self.suite.max_concurrent,
                "graders": list(self.graders.keys()),
            },
        )
    
    def run_sync(self) -> RunnerResult:
        """Synchronous wrapper for run()."""
        return asyncio.run(self.run())


async def run_suite(
    suite_path: Union[str, Path],
    provider: Any,
    *,
    overrides: Optional[Dict[str, Any]] = None,
    verbose: bool = False,
) -> RunnerResult:
    """
    Load and run a suite from a YAML config file.
    
    Args:
        suite_path: Path to suite YAML file
        provider: Model provider instance
        overrides: Optional config overrides
        verbose: Enable verbose logging
    
    Returns:
        RunnerResult with evaluation results
    """
    suite = load_suite(suite_path, overrides)
    runner = EvalRunner(suite, provider, verbose=verbose)
    return await runner.run()


def run_suite_sync(
    suite_path: Union[str, Path],
    provider: Any,
    *,
    overrides: Optional[Dict[str, Any]] = None,
    verbose: bool = False,
) -> RunnerResult:
    """Synchronous version of run_suite()."""
    return asyncio.run(run_suite(suite_path, provider, overrides=overrides, verbose=verbose))
