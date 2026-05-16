import importlib.util
from pathlib import Path
from typing import Any

from runtime.providers.mock import MockProvider


def _import_cs_module():
    repo_root = Path(__file__).resolve().parents[1]
    mod_path = repo_root / "benchmarking" / "cs_eval" / "run_evaluation.py"
    spec = importlib.util.spec_from_file_location("cs_eval_runner_test", str(mod_path))
    assert spec and spec.loader, "Failed to load CS-Eval runner"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def test_cseval_with_local_sample(tmp_path: Any):
    repo_root = Path(__file__).resolve().parents[1]
    sample = repo_root / "benchmarking" / "cs_eval" / "sample_questions.jsonl"
    assert sample.exists(), "Local CS-Eval sample should exist"

    mod = _import_cs_module()
    run_cs_eval_with_provider = getattr(mod, "run_cs_eval_with_provider")
    provider = MockProvider()
    res = run_cs_eval_with_provider(
        provider,
        categories=None,
        max_questions=1,
        batch_size=2,
        output_dir=str(tmp_path),
        verbose=False,
        local_sample_path=str(sample),
    )
    path = Path(res.get("results_path"))
    assert path.exists(), "CS-Eval results should be written for local sample"
