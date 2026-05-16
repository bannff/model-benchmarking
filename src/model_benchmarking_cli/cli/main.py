import click  # type: ignore[reportMissingImports]
from typing import Any, cast

@click.group()
def main():
    """Model Benchmarking CLI"""
    pass

# Help static analyzers understand that `main` is a Click Group with dynamic attributes like `.command()`
main = cast(Any, main)

@main.command()
@click.option("--suite", default="cs-eval", help="Which suite to run (cs-eval|cve-bench|cybergym)")
@click.option("--config", default=None, help="Path to config YAML")
@click.option("--test/--no-test", default=False, help="Run in test mode (no external commands)")
def run(suite: str, config: str | None, test: bool):
    """Run a benchmark suite"""
    from .. import runner
    import sys
    try:
        runner.run_benchmark(suite, config, test_mode=test)
    except Exception as e:
        click.echo(f"Error running benchmark: {e}")
        sys.exit(2)

@main.command()
@click.argument("results_path")
def report(results_path: str):
    """Generate a report from results"""
    from ..report import generate_report
    path = generate_report(results_path)
    click.echo(f"Report generated: {path}")
