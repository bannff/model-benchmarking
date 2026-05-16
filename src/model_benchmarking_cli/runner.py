from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from runtime.config import load_config_file
from runtime.config_models import RootConfig
from runtime.providers.factory import make_provider
from runtime.suites.cs_eval import CSEvalSuite
from runtime.suites.cybergym import CyberGymSuite
from runtime.suites.cve_bench import CVEBenchSuite


@dataclass
class BenchmarkResult:
    name: str
    status: str
    output_path: Optional[str] = None
_SUITE_ALIASES = {
    "cs-eval": "cs-eval",
    "cseval": "cs-eval",
    "cybersec-quiz": "cybersec-quiz",
    "quiz": "cybersec-quiz",
    "cybersec": "cybersec-quiz",
    "cve-bench": "cve-bench",
    "cve": "cve-bench",
}


def _suite_runner(suite: str) -> Callable[..., Any]:
    runners: dict[str, Callable[..., Any]] = {
        "cs-eval": CSEvalSuite,
        "cybergym": CyberGymSuite,
        "cve-bench": CVEBenchSuite,
    }
    if suite == "cybersec-quiz":
        raise ValueError(
            "The legacy cybersec quiz entrypoint is kept only as a local demo helper; "
            "it is no longer dispatched through this compatibility API."
        )
    runner = runners.get(suite)
    if runner is None:
        raise ValueError(f"Unknown suite: {suite}")
    return runner


def run_benchmark(suite: str, config_path: Optional[str] = None, test_mode: bool = False) -> BenchmarkResult:
    """Run a benchmark suite through the current adapter layer.

    The legacy public API is kept for compatibility, but execution now goes
    through the same suite adapters used by the main pipeline instead of stale
    repo-relative shell scripts.
    """
    suite_key = _SUITE_ALIASES.get(suite.lower())
    if suite_key is None:
        raise ValueError(f"Unknown suite: {suite}")
    if test_mode:
        return BenchmarkResult(name=suite_key, status="ok", output_path=None)

    raw_cfg = load_config_file(config_path)
    if not raw_cfg:
        raw_cfg = {"provider": {"name": "mock", "model": "mock"}}
    validated = RootConfig.model_validate(raw_cfg)

    provider_cfg = validated.provider
    provider = make_provider(
        provider_cfg.name,
        model=provider_cfg.model,
        host=provider_cfg.host or "http://localhost:11434",
        use_strands=(provider_cfg.name == "strands-ollama"),
    )

    output_dir = str(validated.pipeline.output_dir)
    runner_cls = _suite_runner(suite_key)
    kwargs: Dict[str, Any] = {"provider": provider, "output_dir": output_dir}
    if runner_cls is CSEvalSuite:
        kwargs.update(
            {
                "categories": validated.pipeline.categories,
                "max_questions": validated.pipeline.max_questions,
                "verbose": validated.pipeline.verbose,
                "cs_eval_config": validated.cs_eval.model_dump(),
            }
        )
    elif runner_cls is CyberGymSuite:
        kwargs.update(
            {
                "max_items": validated.pipeline.max_questions,
                "cybergym_config": validated.cybergym.model_dump(),
            }
        )
    else:
        kwargs.update({"cvebench_config": validated.cvebench.model_dump()})

    import asyncio

    outcome = asyncio.run(runner_cls().run(**kwargs))
    return BenchmarkResult(name=outcome.name, status=outcome.status, output_path=outcome.results_path)
