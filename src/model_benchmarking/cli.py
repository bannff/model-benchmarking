import click
import sys
from . import runner


@click.group()
def main():
    """Model Benchmarking CLI"""
    pass


@main.command()
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


@main.command()
@click.argument("results_path")
def report(results_path: str):
    """Generate a report from results"""
    from .report import generate_report
    path = generate_report(results_path)
    click.echo(f"Report generated: {path}")


@main.command()
@click.option("--provider", default="ollama", help="Model provider (ollama|strands-ollama)")
@click.option("--model", default="llama3.2", help="Model name/id")
@click.option("--host", default="http://localhost:11434", help="Provider host (for Ollama)")
@click.option("--categories", default=None, help="Comma-separated categories (CS-Eval)")
@click.option("--max_questions", default=None, type=int, help="Max questions per category (CS-Eval)")
@click.option("--output_dir", default="results", help="Output directory for artifacts")
@click.option("--verbose/--no-verbose", default=False)
@click.option("--strands-telemetry/--no-strands-telemetry", default=False)
@click.option("--cybergym-mode", type=click.Choice(["sim", "server"]), default="sim", help="CyberGym mode: simulated or server-driven")
@click.option("--cybergym-server", default="http://localhost:8666", help="CyberGym server base URL")
@click.option("--cybergym-data-dir", default=None, help="Path to CyberGym data directory (for task generation)")
@click.option("--cybergym-difficulty", default="level1", help="Task difficulty (level0..level3)")
@click.option("--cvebench-root", default=None, help="Path to local CVE-Bench repository (optional)")
@click.option("--cvebench-model", default=None, help="Model string for CVE-Bench Inspect (optional)")
@click.option("--cvebench-target", multiple=True, help="Repeatable -T flags for Inspect (e.g., challenges=..., variants=one_day)")
def pipeline(provider: str, model: str, host: str, categories: str | None, max_questions: int | None, output_dir: str, verbose: bool, strands_telemetry: bool, cybergym_mode: str, cybergym_server: str, cybergym_data_dir: str | None, cybergym_difficulty: str, cvebench_root: str | None, cvebench_model: str | None, cvebench_target: tuple[str, ...]):
    """Run the full evaluation pipeline: CS-Eval -> CyberGym -> CVE-Bench."""
    from .providers.factory import make_provider
    from .pipeline import run_pipeline

    cats = [c.strip() for c in categories.split(",")] if categories else None
    prov = make_provider(
        provider,
        model=model,
        host=host,
        use_strands=(provider == "strands-ollama"),
    )
    steps = run_pipeline(
        provider=prov,
        categories=cats,
        max_questions=max_questions,
        output_dir=output_dir,
        verbose=verbose,
        use_strands_telemetry=strands_telemetry,
        cybergym_config={
            "mode": cybergym_mode,
            "server_url": cybergym_server,
            "data_dir": cybergym_data_dir,
            "difficulty": cybergym_difficulty,
        },
        cvebench_config={
            "repo_root": cvebench_root,
            "model": cvebench_model,
            "targets": list(cvebench_target) if cvebench_target else [],
        },
    )
    # Compact summary to stdout
    for s in steps:
        click.echo(f"[{s.name}] {s.status} {s.results_path or ''}")
