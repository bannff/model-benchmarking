import click  # type: ignore[reportMissingImports]
import sys
from typing import Any, cast, Optional, List, Dict, Tuple
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
def run(suite: str, config: Optional[str], test: bool):
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
def pipeline(provider: Optional[str], model: str, host: str, categories: Optional[str], max_questions: Optional[int], output_dir: str, verbose: bool, strands_telemetry: bool, cs_eval_local_sample: Optional[str], cybergym_mode: str, cybergym_server: str, cybergym_data_dir: Optional[str], cybergym_difficulty: str, cybergym_use_agent: bool, cvebench_root: Optional[str], cvebench_model: Optional[str], cvebench_target: Tuple[str, ...], skip_cs_eval: bool, skip_cybergym: bool, skip_cve_bench: bool, config: Optional[str], dry_run: bool):
    """Run the full evaluation pipeline: CS-Eval -> CyberGym -> CVE-Bench."""
    from runtime.providers.factory import make_provider
    from .pipeline import run_pipeline
    from runtime.config import load_config_file, deep_merge
    from runtime.config_models import RootConfig
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


# -----------------------------------------------------------------------------
# Evals subcommand group
# -----------------------------------------------------------------------------


@main.group()  # type: ignore[attr-defined]
def evals():
    """Run model evaluations with the evals framework."""
    pass


evals = cast(Any, evals)


@evals.command("run")  # type: ignore[attr-defined]
@click.argument("suite_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--provider", default="ollama", help="Model provider (ollama|mock)")
@click.option("--model", default="llama3.2", help="Model name/id")
@click.option("--host", default="http://localhost:11434", help="Provider host URL")
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


@evals.command("validate")  # type: ignore[attr-defined]
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


@evals.command("list-graders")  # type: ignore[attr-defined]
def evals_list_graders():
    """List available built-in grader functions."""
    from runtime.evals.graders import GraderRegistry
    
    click.echo("Tool Grader Functions:")
    click.echo("-" * 40)
    for name, desc in sorted(GraderRegistry.list_tool_functions().items()):
        click.echo(f"  {name}: {desc}")


@evals.command("list-extractors")  # type: ignore[attr-defined]
def evals_list_extractors():
    """List available extractors."""
    from runtime.evals.extractors import ExtractorRegistry
    
    click.echo("Available Extractors:")
    click.echo("-" * 40)
    for name in ExtractorRegistry.list_extractors():
        click.echo(f"  {name}")


# -----------------------------------------------------------------------------
# Taxonomy subcommand group
# -----------------------------------------------------------------------------


@main.group()  # type: ignore[attr-defined]
def taxonomy():
    """Manage and explore taxonomies for evaluation classification."""
    pass


taxonomy = cast(Any, taxonomy)


@taxonomy.command("list")  # type: ignore[attr-defined]
def taxonomy_list():
    """List all registered taxonomies."""
    from runtime.taxonomy import list_taxonomies, get_taxonomy
    
    click.echo("Registered Taxonomies:")
    click.echo("-" * 40)
    for name in list_taxonomies():
        tax = get_taxonomy(name)
        if tax:
            click.echo(f"  {name} (v{tax.version})")
            if tax.description:
                click.echo(f"    {tax.description}")


@taxonomy.command("show")  # type: ignore[attr-defined]
@click.argument("taxonomy_name", default="cybersecurity")
@click.option("--dimension", "-d", default=None, help="Show only this dimension")
def taxonomy_show(taxonomy_name: str, dimension: Optional[str]):
    """Show taxonomy structure and dimensions."""
    from runtime.taxonomy import get_taxonomy
    
    tax = get_taxonomy(taxonomy_name)
    if tax is None:
        click.echo(f"Taxonomy not found: {taxonomy_name}", err=True)
        sys.exit(1)
    
    click.echo(f"Taxonomy: {tax.name} (v{tax.version})")
    if tax.description:
        click.echo(f"Description: {tax.description}")
    click.echo("")
    
    dims_to_show = [tax.dimensions[dimension]] if dimension and dimension in tax.dimensions else list(tax.dimensions.values())
    
    for dim in dims_to_show:
        click.echo(f"[{dim.id}] {dim.name}")
        if dim.description:
            click.echo(f"  {dim.description}")
        click.echo(f"  Required: {dim.required}, Multi-select: {dim.multi_select}")
        click.echo("  Values:")
        
        for node_path, node in dim.flatten().items():
            indent = "    " + "  " * node_path.count(".")
            click.echo(f"{indent}{node_path}: {node.name}")
        
        click.echo("")


@taxonomy.command("validate")  # type: ignore[attr-defined]
@click.argument("labels", nargs=-1)
@click.option("--taxonomy", "-t", "taxonomy_name", default="cybersecurity", help="Taxonomy to validate against")
def taxonomy_validate(labels: Tuple[str, ...], taxonomy_name: str):
    """Validate taxonomy labels (format: dimension=value)."""
    from runtime.taxonomy import get_taxonomy
    
    tax = get_taxonomy(taxonomy_name)
    if tax is None:
        click.echo(f"Taxonomy not found: {taxonomy_name}", err=True)
        sys.exit(1)
    
    parsed: dict[str, str | list[str]] = {}
    for label in labels:
        if "=" not in label:
            click.echo(f"Invalid format: {label} (expected dimension=value)", err=True)
            sys.exit(1)
        dim, val = label.split("=", 1)
        if dim in parsed:
            existing = parsed[dim]
            if isinstance(existing, list):
                existing.append(val)
            else:
                parsed[dim] = [existing, val]
        else:
            parsed[dim] = val
    
    errors = tax.validate_labels(parsed)
    
    if errors:
        click.echo("Validation FAILED:", err=True)
        for error in errors:
            click.echo(f"  - {error}", err=True)
        sys.exit(1)
    else:
        click.echo("✓ Labels are valid")


@taxonomy.command("map")  # type: ignore[attr-defined]
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option("--mapper", "-m", default="auto", help="Mapper to use: 'auto', 'cs_eval', 'cybergym', 'cve_bench', or path to YAML")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output enriched dataset to file")
@click.option("--preview", type=int, default=5, help="Number of samples to preview")
def taxonomy_map(dataset_path: str, mapper: str, output: Optional[str], preview: int):
    """Map taxonomy labels to samples in a dataset."""
    import json as _json
    from runtime.taxonomy import AutoMapper, TaxonomyMapper, create_cs_eval_mapper, create_cybergym_mapper, create_cve_bench_mapper
    from runtime.evals.dataset import load_dataset_list
    
    # Create mapper
    if mapper == "auto":
        tax_mapper = AutoMapper()
        rule_mapper = None
    elif mapper == "cs_eval":
        tax_mapper = AutoMapper()
        rule_mapper = create_cs_eval_mapper()
    elif mapper == "cybergym":
        tax_mapper = AutoMapper()
        rule_mapper = create_cybergym_mapper()
    elif mapper == "cve_bench":
        tax_mapper = AutoMapper()
        rule_mapper = create_cve_bench_mapper()
    else:
        # Assume it's a path to YAML
        tax_mapper = AutoMapper()
        rule_mapper = TaxonomyMapper.from_yaml(mapper)
    
    # Load dataset
    try:
        samples = load_dataset_list(dataset_path)
    except Exception as e:
        click.echo(f"Error loading dataset: {e}", err=True)
        sys.exit(1)
    
    click.echo(f"Loaded {len(samples)} samples from {dataset_path}")
    
    # Map samples
    enriched_samples = []
    for sample in samples:
        sample_dict = sample.model_dump()
        
        # Apply rule-based mapping first if available
        if rule_mapper:
            mapped = rule_mapper.map(sample_dict)
            sample_dict["taxonomy"] = mapped.labels
        
        # Enrich with auto-inference
        inferred = tax_mapper.infer(sample_dict)
        if "taxonomy" in sample_dict and sample_dict["taxonomy"]:
            # Merge: existing takes precedence
            for dim, val in inferred.labels.items():
                if dim not in sample_dict["taxonomy"]:
                    sample_dict["taxonomy"][dim] = val
        else:
            sample_dict["taxonomy"] = inferred.labels
        
        enriched_samples.append(sample_dict)
    
    # Preview
    click.echo(f"\nPreview ({min(preview, len(enriched_samples))} samples):")
    click.echo("-" * 60)
    for i, sample in enumerate(enriched_samples[:preview]):
        click.echo(f"\n[{i+1}] ID: {sample.get('id')}")
        click.echo(f"    Input: {sample.get('input', '')[:80]}...")
        click.echo(f"    Taxonomy: {sample.get('taxonomy', {})}")
    
    # Output if specified
    if output:
        with open(output, "w", encoding="utf-8") as f:
            for sample in enriched_samples:
                f.write(_json.dumps(sample) + "\n")
        click.echo(f"\n✓ Enriched dataset saved to: {output}")
