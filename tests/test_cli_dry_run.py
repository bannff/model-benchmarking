import json
from click.testing import CliRunner
from mcp.cli import main

def test_pipeline_dry_run_shows_plan(tmp_path):
    runner = CliRunner()
    cfg = {
        "provider": {"name": "mock", "model": "mock"},
        "pipeline": {"output_dir": str(tmp_path / "out"), "skip_cybergym": True, "skip_cve_bench": True},
    }
    with runner.isolated_filesystem():
        # write a temp config
        import pathlib
        p = pathlib.Path("cfg.json")
        p.write_text(json.dumps(cfg))
        res = runner.invoke(main, ["pipeline", "--config", str(p), "--dry-run"])
        assert res.exit_code == 0
        assert "Planned steps:" in res.output
        assert "cs-eval" in res.output
