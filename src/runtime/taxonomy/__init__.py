"""
Taxonomy package for standardized classification of evaluation samples.

Provides:
- Schema definitions for taxonomy dimensions
- Registry for loading and validating taxonomies
- Mapping utilities for classifying samples
- Aggregation helpers for taxonomy-based metrics
"""
from __future__ import annotations

from .schema import (
    TaxonomyNode,
    TaxonomyDimension,
    TaxonomySpec,
    SampleTaxonomy,
)
from .registry import (
    TaxonomyRegistry,
    get_taxonomy,
    list_taxonomies,
    register_taxonomy,
)
from .mapper import (
    MappingRule,
    TaxonomyMapper,
    AutoMapper,
    mapper_registry,
    create_cs_eval_mapper,
    create_cybergym_mapper,
    create_cve_bench_mapper,
)

__all__ = [
    # Schema
    "TaxonomyNode",
    "TaxonomyDimension",
    "TaxonomySpec",
    "SampleTaxonomy",
    # Registry
    "TaxonomyRegistry",
    "get_taxonomy",
    "list_taxonomies",
    "register_taxonomy",
    # Mapper
    "MappingRule",
    "TaxonomyMapper",
    "AutoMapper",
    "mapper_registry",
    "create_cs_eval_mapper",
    "create_cybergym_mapper",
    "create_cve_bench_mapper",
]
