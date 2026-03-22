import importlib.util
from pathlib import Path
from typing import Any

from runtime.providers.mock import MockProvider


def _import_cg_module():
    repo_root = Path(__file__).resolve().parents[1]
    mod_path = repo_root / "benchmarking" / "cybergym" / "evaluator.py"
    spec = importlib.util.spec_from_file_location("cybergym_evaluator_test", str(mod_path))
    assert spec and spec.loader, "Failed to load CyberGym evaluator module"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def _sample_path() -> str:
    repo_root = Path(__file__).resolve().parents[1]
    p1 = repo_root / "benchmarking" / "cybergym" / "cybergym_subset_sample.json"
    if p1.exists():
        return str(p1)
    p2 = repo_root / "benchmarking" / "cybergym" / "cybergym" / "cybergym_subset_sample.json"
    return str(p2)


def _run_mode(mode: str, tmp_path: Any):
    mod = _import_cg_module()
    run_cybergym_with_provider = getattr(mod, "run_cybergym_with_provider")
    provider = MockProvider()
    res = run_cybergym_with_provider(
        provider,
        sample_file=_sample_path(),
        output_dir=str(tmp_path),
        max_items=1,
        cybergym_config={"mode": mode},
    )
    out_path = Path(res["results_path"]) 
    assert out_path.exists(), f"cybergym_results.json not written for mode={mode}"
    metrics = res.get("metrics", {})
    assert metrics.get("total_tasks") == 1
    assert 0.0 <= float(metrics.get("success_rate", 0.0)) <= 1.0


def test_cybergym_sim_mode(tmp_path: Any):
    _run_mode("sim", tmp_path)


def test_cybergym_server_mode(tmp_path: Any):
    _run_mode("server", tmp_path)
