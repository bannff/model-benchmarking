import click
import sys
from typing import Optional, Tuple, Any, cast

@click.group()
def taxonomy():
    """Manage and explore taxonomies for evaluation classification."""
    pass

# Help static analyzers understand that `taxonomy` is a Click Group
taxonomy = cast(Any, taxonomy)

@taxonomy.command("list")
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


@taxonomy.command("show")
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


@taxonomy.command("validate")
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


@taxonomy.command("map")
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option("--mapper", "-m", default="auto", help="Mapper to use: 'auto', 'cs_eval', 'cybergym', 'cve_bench', or path to YAML")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output enriched dataset to file")
@click.option("--preview", type=int, default=5, help="Number of samples to preview")
def taxonomy_map(dataset_path: str, mapper: str, output: Optional[str], preview: int):
    """Map taxonomy labels to samples in a dataset."""
    import json as _json
    from runtime.taxonomy import AutoMapper, TaxonomyMapper, mapper_registry
    from runtime.evals.dataset.core import load_dataset_list
    
    # Create mapper
    tax_mapper = AutoMapper()
    if mapper == "auto":
        rule_mapper = None
    else:
        mapper_factory = mapper_registry.get(mapper)
        rule_mapper = mapper_factory() if mapper_factory else TaxonomyMapper.from_yaml(mapper)
    
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
