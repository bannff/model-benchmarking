import click
import sys
from typing import Optional, Any, cast
from runtime.constants import DEFAULT_MODEL, DEFAULT_OLLAMA_HOST

@click.group()
def evals():
    """Run model evaluations with the evals framework."""
    pass

# Help static analyzers understand that `evals` is a Click Group
evals = cast(Any, evals)

@evals.command("run")
@click.argument("suite_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--provider", default="ollama", help="Model provider (ollama|mock)")
@click.option("--model", default=DEFAULT_MODEL, help="Model name/id")
@click.option("--host", default=DEFAULT_OLLAMA_HOST, help="Provider host URL")
@click.option("--max-samples", type=int, default=None, help="Maximum samples to evaluate")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output file for results (JSON)")
@click.option("--verbose/--no-verbose", default=False, help="Enable verbose logging")
def evals_run(suite_path: str, provider: str, model: str, host: str, max_samples: Optional[int], output: Optional[str], verbose: bool):
    """Run an evaluation suite from a YAML config file."""
    import asyncio
    import json as _json
    from runtime.providers.factory import make_provider
    from runtime.evals import run_suite
    
    # Create provider
    prov = make_provider(provider, model=model, host=host)
    
    # Build overrides
    overrides = {}
    if max_samples:
        overrides["max_samples"] = max_samples
    
    # Run evaluation
    try:
        result = asyncio.run(run_suite(suite_path, prov, overrides=overrides, verbose=verbose))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)
    
    # Display results
    click.echo(f"\n{'='*60}")
    click.echo(f"Suite: {result.suite_name}")
    click.echo(f"Model: {result.model_name}")
    click.echo(f"{'='*60}")
    click.echo(f"Total samples: {result.metrics.total}")
    click.echo(f"Attempted: {result.metrics.attempted}")
    click.echo(f"Failed: {result.metrics.failed}")
    click.echo(f"Average score: {result.metrics.avg_score:.4f}")
    click.echo(f"Pass rate: {result.metrics.pass_rate:.2%}")
    click.echo(f"{'='*60}")
    click.echo(f"Gate: {'✓ PASSED' if result.gate_passed else '✗ FAILED'}")
    if result.gate_details:
        click.echo(f"  {result.gate_details}")
    click.echo(f"{'='*60}\n")
    
    # Save results if output specified
    if output:
        with open(output, "w", encoding="utf-8") as f:
            _json.dump(result.model_dump(), f, indent=2, default=str)
        click.echo(f"Results saved to: {output}")
    
    # Exit with appropriate code
    sys.exit(0 if result.gate_passed else 1)


@evals.command("validate")
@click.argument("suite_path", type=click.Path(exists=True, dir_okay=False))
def evals_validate(suite_path: str):
    """Validate a suite configuration without running it."""
    from runtime.evals.suite import SuiteLoader
    
    errors = SuiteLoader.validate(suite_path)
    
    if errors:
        click.echo("Validation FAILED:", err=True)
        for error in errors:
            click.echo(f"  - {error}", err=True)
        sys.exit(1)
    else:
        click.echo("✓ Suite configuration is valid")
        
        # Show summary
        suite = SuiteLoader.load(suite_path)
        click.echo(f"\nSuite: {suite.name}")
        click.echo(f"Dataset: {suite.dataset}")
        click.echo(f"Graders: {', '.join(suite.graders.keys())}")
        click.echo(f"Gate: {suite.gate.metric_key} {suite.gate.op.value} {suite.gate.value}")


@evals.command("list-graders")
def evals_list_graders():
    """List available built-in grader functions."""
    from runtime.evals.graders import GraderRegistry
    
    click.echo("Tool Grader Functions:")
    click.echo("-" * 40)
    for name, desc in sorted(GraderRegistry.list_tool_functions().items()):
        click.echo(f"  {name}: {desc}")


@evals.command("list-extractors")
def evals_list_extractors():
    """List available extractors."""
    from runtime.evals.extractors import ExtractorRegistry
    
    click.echo("Available Extractors:")
    click.echo("-" * 40)
    for name in ExtractorRegistry.list_extractors():
        click.echo(f"  {name}")
