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
@click.option("--cybergym-use-agent/--no-cybergym-use-agent", default=False, help="Use agent workflow (Strands + sandbox) for CyberGym tasks")
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
@click.option("--dry-run/--no-dry-run", default=False, help="Validate and print resolved config; do not execute")
def pipeline(provider: str | None, model: str, host: str, categories: str | None, max_questions: int | None, output_dir: str, verbose: bool, strands_telemetry: bool, cs_eval_local_sample: str | None, cybergym_mode: str, cybergym_server: str, cybergym_data_dir: str | None, cybergym_difficulty: str, cybergym_use_agent: bool, cvebench_root: str | None, cvebench_model: str | None, cvebench_target: tuple[str, ...], skip_cs_eval: bool, skip_cybergym: bool, skip_cve_bench: bool, config: str | None, dry_run: bool):
    """Run the full evaluation pipeline: CS-Eval -> CyberGym -> CVE-Bench."""
    from .providers.factory import make_provider
    from .pipeline import run_pipeline
    from .config import load_config_file, deep_merge
    from .config_models import RootConfig
    import json as _json

    # Load config file and merge CLI overrides
    file_cfg = load_config_file(config)
    provider_overrides = {}
    if provider is not None:
        provider_overrides["name"] = provider
    if model != "llama3.2":
        provider_overrides["model"] = model
    if host != "http://localhost:11434":
        provider_overrides["host"] = host

    pipeline_overrides = {}
    if categories:
        pipeline_overrides["categories"] = [c.strip() for c in categories.split(",")]
    if max_questions is not None:
        pipeline_overrides["max_questions"] = max_questions
    if output_dir != "results":
        pipeline_overrides["output_dir"] = output_dir
    if verbose:
        pipeline_overrides["verbose"] = verbose
    if strands_telemetry:
        pipeline_overrides["use_strands_telemetry"] = strands_telemetry
    if skip_cs_eval:
        pipeline_overrides["skip_cs_eval"] = True
    if skip_cybergym:
        pipeline_overrides["skip_cybergym"] = True
    if skip_cve_bench:
        pipeline_overrides["skip_cve_bench"] = True

    cs_eval_overrides = {}
    if cs_eval_local_sample:
        cs_eval_overrides["local_sample_path"] = cs_eval_local_sample

    cybergym_overrides = {}
    if cybergym_mode != "sim":
        cybergym_overrides["mode"] = cybergym_mode
    if cybergym_server != "http://localhost:8666":
        cybergym_overrides["server_url"] = cybergym_server
    if cybergym_data_dir:
        cybergym_overrides["data_dir"] = cybergym_data_dir
    if cybergym_difficulty != "level1":
        cybergym_overrides["difficulty"] = cybergym_difficulty
    if cybergym_use_agent:
        cybergym_overrides["use_agent_workflow"] = True

    cvebench_overrides = {}
    if cvebench_root:
        cvebench_overrides["repo_root"] = cvebench_root
    if cvebench_model:
        cvebench_overrides["model"] = cvebench_model
    if cvebench_target:
        cvebench_overrides["targets"] = list(cvebench_target)

    cli_cfg = {}
    if provider_overrides:
        cli_cfg["provider"] = provider_overrides
    if pipeline_overrides:
        cli_cfg["pipeline"] = pipeline_overrides
    if cs_eval_overrides:
        cli_cfg["cs_eval"] = cs_eval_overrides
    if cybergym_overrides:
        cli_cfg["cybergym"] = cybergym_overrides
    if cvebench_overrides:
        cli_cfg["cvebench"] = cvebench_overrides
    cfg = deep_merge(file_cfg, cli_cfg)
    # Validate and normalize with Pydantic
    validated = RootConfig.model_validate(cfg).model_dump()

    if dry_run:
        click.echo("Resolved and validated config:")
        click.echo(_json.dumps(validated, indent=2))
        planned_steps = [
            s for s, flag in (
                ("cs-eval", not validated["pipeline"]["skip_cs_eval"]),
                ("cybergym", not validated["pipeline"]["skip_cybergym"]),
                ("cve-bench", not validated["pipeline"]["skip_cve_bench"]),
            ) if flag
        ]
        click.echo(f"Planned steps: {', '.join(planned_steps) if planned_steps else 'none'}")
        return

    # Construct provider (CLI overrides take precedence if provided)
    prov_name = (validated.get("provider", {}) or {}).get("name") or "ollama"
    prov = make_provider(
        prov_name,
        model=(validated.get("provider", {}) or {}).get("model") or model,
        host=(validated.get("provider", {}) or {}).get("host") or host,
        use_strands=(prov_name == "strands-ollama"),
    )
    steps = run_pipeline(
        provider=prov,
        categories=(validated.get("pipeline", {}) or {}).get("categories"),
        max_questions=(validated.get("pipeline", {}) or {}).get("max_questions"),
        output_dir=(validated.get("pipeline", {}) or {}).get("output_dir", output_dir),
        verbose=bool((validated.get("pipeline", {}) or {}).get("verbose", verbose)),
        use_strands_telemetry=bool((validated.get("pipeline", {}) or {}).get("use_strands_telemetry", strands_telemetry)),
        skip_cs_eval=bool((validated.get("pipeline", {}) or {}).get("skip_cs_eval", skip_cs_eval)),
        skip_cybergym=bool((validated.get("pipeline", {}) or {}).get("skip_cybergym", False)),
        skip_cvebench=bool((validated.get("pipeline", {}) or {}).get("skip_cve_bench", False)),
        cs_eval_config=(validated.get("cs_eval", {}) or {}),
        cybergym_config=(validated.get("cybergym", {}) or {}),
        cvebench_config=(validated.get("cvebench", {}) or {}),
    )
    # Compact summary to stdout
    for s in steps:
        click.echo(f"[{s.name}] {s.status} {s.results_path or ''}")
