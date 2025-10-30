import click  # type: ignore[reportMissingImports]
import sys
from typing import Any, cast
from . import runner


@click.group()
def main():
    """Model Benchmarking CLI"""
    pass


# Help static analyzers understand that `main` is a Click Group with dynamic attributes like `.command()`
main = cast(Any, main)

@main.command()  # type: ignore[attr-defined]
@click.option("--suite", default="cs-eval", help="Which suite to run (cs-eval|cve-bench|cybergym)")
@click.option("--config", default=None, help="Path to config YAML")
@click.option("--test/--no-test", default=False, help="Run in test mode (no external commands)")
def run(suite: str, config: str | None, test: bool):
    """Run a benchmark suite"""
    try:
        runner.run_benchmark(suite, config, test_mode=test)
    except Exception as e:
        click.echo(f"Error running benchmark: {e}")
        sys.exit(2)


@main.command()  # type: ignore[attr-defined]
@click.argument("results_path")
def report(results_path: str):
    """Generate a report from results"""
    from .report import generate_report
    path = generate_report(results_path)
    click.echo(f"Report generated: {path}")


@main.command()  # type: ignore[attr-defined]
@click.option("--provider", default=None, help="Model provider (ollama|strands-ollama|mock) [overrides config]")
@click.option("--model", default="llama3.2", help="Model name/id")
@click.option("--host", default="http://localhost:11434", help="Provider host (for Ollama)")
@click.option("--categories", default=None, help="Comma-separated categories (CS-Eval)")
@click.option("--max_questions", default=None, type=int, help="Max questions per category (CS-Eval)")
@click.option("--output_dir", default="results", help="Output directory for artifacts")
@click.option("--verbose/--no-verbose", default=False)
@click.option("--strands-telemetry/--no-strands-telemetry", default=False)
@click.option("--cs-eval-local-sample", type=click.Path(exists=True, dir_okay=False), default=None, help="Path to local CS-Eval sample (JSON/JSONL)")
@click.option("--cybergym-mode", type=click.Choice(["sim", "server"]), default="sim", help="CyberGym mode: simulated or server-driven")
@click.option("--cybergym-server", default="http://localhost:8666", help="CyberGym server base URL")
@click.option("--cybergym-data-dir", default=None, help="Path to CyberGym data directory (for task generation)")
@click.option("--cybergym-difficulty", default="level1", help="Task difficulty (level0..level3)")
@click.option("--cvebench-root", default=None, help="Path to local CVE-Bench repository (optional)")
@click.option("--cvebench-model", default=None, help="Model string for CVE-Bench Inspect (optional)")
@click.option("--cvebench-target", multiple=True, help="Repeatable -T flags for Inspect (e.g., challenges=..., variants=one_day)")
@click.option("--skip-cs-eval/--no-skip-cs-eval", default=False, help="Skip the CS-Eval step (useful for offline runs)")
@click.option("--skip-cybergym/--no-skip-cybergym", default=False, help="Skip the CyberGym step")
@click.option("--skip-cve-bench/--no-skip-cve-bench", default=False, help="Skip the CVE-Bench step")
@click.option("--config", type=click.Path(exists=True, dir_okay=False), default=None, help="Path to pipeline config (YAML/JSON/TOML)")
def pipeline(provider: str | None, model: str, host: str, categories: str | None, max_questions: int | None, output_dir: str, verbose: bool, strands_telemetry: bool, cs_eval_local_sample: str | None, cybergym_mode: str, cybergym_server: str, cybergym_data_dir: str | None, cybergym_difficulty: str, cvebench_root: str | None, cvebench_model: str | None, cvebench_target: tuple[str, ...], skip_cs_eval: bool, skip_cybergym: bool, skip_cve_bench: bool, config: str | None):
    """Run the full evaluation pipeline: CS-Eval -> CyberGym -> CVE-Bench."""
    from .providers.factory import make_provider
    from .pipeline import run_pipeline
    from .config import load_config_file, deep_merge

    # Load config file and merge CLI overrides
    file_cfg = load_config_file(config)
    cli_cfg = {
        "provider": {
            "name": provider,
            "model": model,
            "host": host,
        },
        "pipeline": {
            "categories": [c.strip() for c in categories.split(",")] if categories else None,
            "max_questions": max_questions,
            "output_dir": output_dir,
            "verbose": verbose,
            "use_strands_telemetry": strands_telemetry,
            "skip_cs_eval": skip_cs_eval,
            "skip_cybergym": skip_cybergym,
            "skip_cve_bench": skip_cve_bench,
        },
        "cs_eval": {
            "local_sample_path": cs_eval_local_sample,
        },
        "cybergym": {
            "mode": cybergym_mode,
            "server_url": cybergym_server,
            "data_dir": cybergym_data_dir,
            "difficulty": cybergym_difficulty,
        },
        "cvebench": {
            "repo_root": cvebench_root,
            "model": cvebench_model,
            "targets": list(cvebench_target) if cvebench_target else [],
        },
    }
    cfg = deep_merge(file_cfg, cli_cfg)

    # Construct provider (CLI overrides take precedence if provided)
    prov_name = (cfg.get("provider", {}) or {}).get("name") or "ollama"
    prov = make_provider(
        prov_name,
        model=(cfg.get("provider", {}) or {}).get("model") or model,
        host=(cfg.get("provider", {}) or {}).get("host") or host,
        use_strands=(prov_name == "strands-ollama"),
    )
    steps = run_pipeline(
        provider=prov,
        categories=(cfg.get("pipeline", {}) or {}).get("categories"),
        max_questions=(cfg.get("pipeline", {}) or {}).get("max_questions"),
        output_dir=(cfg.get("pipeline", {}) or {}).get("output_dir", output_dir),
        verbose=bool((cfg.get("pipeline", {}) or {}).get("verbose", verbose)),
        use_strands_telemetry=bool((cfg.get("pipeline", {}) or {}).get("use_strands_telemetry", strands_telemetry)),
        skip_cs_eval=bool((cfg.get("pipeline", {}) or {}).get("skip_cs_eval", skip_cs_eval)),
        skip_cybergym=bool((cfg.get("pipeline", {}) or {}).get("skip_cybergym", False)),
        skip_cvebench=bool((cfg.get("pipeline", {}) or {}).get("skip_cve_bench", False)),
        cs_eval_config=(cfg.get("cs_eval", {}) or {}),
        cybergym_config=(cfg.get("cybergym", {}) or {}),
        cvebench_config=(cfg.get("cvebench", {}) or {}),
    )
    # Compact summary to stdout
    for s in steps:
        click.echo(f"[{s.name}] {s.status} {s.results_path or ''}")
