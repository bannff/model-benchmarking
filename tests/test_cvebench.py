import importlib.util
from pathlib import Path
from typing import Any

from runtime.providers.mock import MockProvider


def _import_cve_module():
    repo_root = Path(__file__).resolve().parents[1]
    mod_path = repo_root / "benchmarking" / "cve_bench" / "evaluator.py"
    spec = importlib.util.spec_from_file_location("cve_evaluator_test", str(mod_path))
    assert spec and spec.loader, "Failed to load CVE-Bench evaluator module"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def test_cvebench_run_placeholder(tmp_path: Any):
    mod = _import_cve_module()
    run_cve_bench = getattr(mod, "run_cve_bench")
    provider = MockProvider()
    res = run_cve_bench(output_dir=str(tmp_path), cvebench_config={"targets": []}, provider=provider)
    out_path = Path(res["results_path"])
    assert out_path.exists(), "cve_bench_results.json should be written"
    metrics = res.get("metrics", {})
    assert "invocation_status" in metrics
    # Placeholder script exits 0 in repo, so status should start with ok
    assert str(metrics["invocation_status"]).startswith("ok") or str(metrics["invocation_status"]).startswith("exit")
