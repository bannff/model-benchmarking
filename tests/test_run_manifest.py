import json
from pathlib import Path
from model_benchmarking.providers.factory import make_provider
from model_benchmarking.pipeline import run_pipeline


def test_pipeline_writes_manifest(tmp_path: Path):
    out = tmp_path / "results"
    prov = make_provider("mock", model="mock")
    steps = run_pipeline(
        provider=prov,
        categories=None,
        max_questions=1,
        output_dir=str(out),
        verbose=False,
        skip_cs_eval=True,  # keep fast
        skip_cybergym=True,
        skip_cvebench=True,
    )
    assert steps and steps[0].status == "skipped"
    manifest = list(out.glob("manifest_*.json"))
    assert manifest, "Expected a manifest_*.json file in output_dir"
    data = json.loads(manifest[0].read_text())
    assert data.get("suite") == "pipeline"
    assert data.get("status") in {"ok", "failed"}
    # index appended
    index = out / "index.jsonl"
    assert index.exists()
    assert index.read_text().strip(), "index.jsonl should not be empty"
