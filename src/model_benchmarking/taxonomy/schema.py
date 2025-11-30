"""
Taxonomy schema definitions.

Defines the core data structures for hierarchical taxonomies:
- TaxonomyNode: A single node in a taxonomy tree (e.g., "buffer_overflow" under "memory_safety")
- TaxonomyDimension: A classification dimension (e.g., "capability", "domain", "cwe")
- TaxonomySpec: Complete taxonomy specification with multiple dimensions
- SampleTaxonomy: Taxonomy labels applied to a specific sample
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast
from pydantic import BaseModel, Field, field_validator


class TaxonomyNode(BaseModel):
    """
    A single node in a taxonomy hierarchy.
    
    Nodes can have children for nested classification.
    Example: exploit_development -> buffer_overflow -> stack_based
    """
    
    id: str = Field(
        description="Unique identifier for this node (snake_case)"
    )
    name: str = Field(
        description="Human-readable display name"
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of what this node represents"
    )
    aliases: List[str] = Field(
        default_factory=list,
        description="Alternative names/terms that map to this node"
    )
    children: List["TaxonomyNode"] = Field(
        default_factory=list,
        description="Child nodes in the hierarchy"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (e.g., CWE ID, MITRE ATT&CK ID)"
    )
    
    @field_validator("id", mode="before")
    @classmethod
    def normalize_id(cls, v: str) -> str:
        """Normalize ID to lowercase with underscores."""
        return str(v).lower().replace("-", "_").replace(" ", "_")
    
    def flatten(self, prefix: str = "") -> Dict[str, "TaxonomyNode"]:
        """
        Flatten the tree into a dict of full_path -> node.
        
        Example: {"exploit_development.buffer_overflow": node}
        """
        result: Dict[str, TaxonomyNode] = {}
        full_id = f"{prefix}.{self.id}" if prefix else self.id
        result[full_id] = self
        
        for child in self.children:
            result.update(child.flatten(full_id))
        
        return result
    
    def get_all_aliases(self) -> Set[str]:
        """Get all aliases including the ID and name."""
        aliases = {self.id, self.name.lower()}
        aliases.update(a.lower() for a in self.aliases)
        return aliases


class TaxonomyDimension(BaseModel):
    """
    A classification dimension within the taxonomy.
    
    Examples:
    - capability: What skill is being evaluated (exploit_development, forensics, etc.)
    - domain: Security domain (network, web, binary, cloud)
    - difficulty: Normalized difficulty levels
    - cwe: CWE weakness classification
    - attack_stage: MITRE ATT&CK kill chain stage
    """
    
    id: str = Field(
        description="Dimension identifier (e.g., 'capability', 'domain')"
    )
    name: str = Field(
        description="Human-readable dimension name"
    )
    description: Optional[str] = Field(
        default=None,
        description="What this dimension classifies"
    )
    required: bool = Field(
        default=False,
        description="Whether samples must have a value for this dimension"
    )
    multi_select: bool = Field(
        default=False,
        description="Whether samples can have multiple values for this dimension"
    )
    nodes: List[TaxonomyNode] = Field(
        default_factory=list,
        description="Top-level nodes in this dimension"
    )
    
    @field_validator("id", mode="before")
    @classmethod
    def normalize_id(cls, v: str) -> str:
        return str(v).lower().replace("-", "_").replace(" ", "_")
    
    def flatten(self) -> Dict[str, TaxonomyNode]:
        """Flatten all nodes in this dimension."""
        result: Dict[str, TaxonomyNode] = {}
        for node in self.nodes:
            result.update(node.flatten())
        return result
    
    def get_node(self, node_id: str) -> Optional[TaxonomyNode]:
        """Get a node by ID (supports dot notation for nested nodes)."""
        flattened = self.flatten()
        # Try exact match first
        if node_id in flattened:
            return flattened[node_id]
        # Try case-insensitive
        normalized = node_id.lower().replace("-", "_").replace(" ", "_")
        for key, node in flattened.items():
            if key.lower() == normalized:
                return node
        return None
    
    def validate_value(self, value: str) -> bool:
        """Check if a value is valid for this dimension."""
        return self.get_node(value) is not None
    
    def get_valid_values(self) -> List[str]:
        """Get all valid values (full paths) for this dimension."""
        return list(self.flatten().keys())


class TaxonomySpec(BaseModel):
    """
    Complete taxonomy specification.
    
    A taxonomy has:
    - name and version for identification
    - Multiple dimensions for classification
    - Optional parent taxonomy for inheritance
    """
    
    name: str = Field(
        description="Taxonomy name (e.g., 'cybersecurity')"
    )
    version: str = Field(
        default="1.0.0",
        description="Semantic version"
    )
    description: Optional[str] = Field(
        default=None,
        description="What this taxonomy covers"
    )
    parent: Optional[str] = Field(
        default=None,
        description="Parent taxonomy to inherit from"
    )
    dimensions: Dict[str, TaxonomyDimension] = Field(
        default_factory=dict,
        description="Dimension ID -> dimension spec"
    )
    
    @field_validator("dimensions", mode="before")
    @classmethod
    def parse_dimensions(cls, v: Any) -> Dict[str, TaxonomyDimension]:
        """Parse dimensions from dict or list format."""
        if isinstance(v, dict):
            result: Dict[str, TaxonomyDimension] = {}
            items = cast(List[Tuple[str, Any]], list(v.items()))
            for key, dim in items:
                key_str = str(key)
                if isinstance(dim, TaxonomyDimension):
                    result[key_str] = dim
                elif isinstance(dim, dict):
                    dim_items = cast(List[Tuple[str, Any]], list(dim.items()))
                    dim_dict: Dict[str, Any] = {str(k): val for k, val in dim_items}
                    if "id" not in dim_dict:
                        dim_dict["id"] = key_str
                    result[key_str] = TaxonomyDimension(**dim_dict)
                else:
                    raise ValueError(f"Invalid dimension: {dim}")
            return result
        elif isinstance(v, list):
            dims = [d for d in v if isinstance(d, TaxonomyDimension)]
            return {d.id: d for d in dims}
        return cast(Dict[str, TaxonomyDimension], v)
    
    def get_dimension(self, dim_id: str) -> Optional[TaxonomyDimension]:
        """Get a dimension by ID."""
        return self.dimensions.get(dim_id)
    
    def validate_labels(self, labels: Dict[str, Union[str, List[str]]]) -> List[str]:
        """
        Validate a set of taxonomy labels.
        
        Returns list of validation errors (empty if valid).
        """
        errors: List[str] = []
        
        # Check required dimensions
        for dim_id, dim in self.dimensions.items():
            if dim.required and dim_id not in labels:
                errors.append(f"Missing required dimension: {dim_id}")
        
        # Validate provided labels
        for dim_id, values in labels.items():
            dim = self.dimensions.get(dim_id)
            if dim is None:
                errors.append(f"Unknown dimension: {dim_id}")
                continue
            
            # Normalize to list
            value_list = [values] if isinstance(values, str) else values
            
            if not dim.multi_select and len(value_list) > 1:
                errors.append(f"Dimension '{dim_id}' does not allow multiple values")
            
            for val in value_list:
                if not dim.validate_value(val):
                    errors.append(f"Invalid value '{val}' for dimension '{dim_id}'")
        
        return errors
    
    def list_dimensions(self) -> List[str]:
        """List all dimension IDs."""
        return list(self.dimensions.keys())


class SampleTaxonomy(BaseModel):
    """
    Taxonomy labels applied to a specific sample.
    
    Stores dimension -> value(s) mapping with validation.
    """
    
    labels: Dict[str, Union[str, List[str]]] = Field(
        default_factory=dict,
        description="Dimension ID -> value(s)"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the classification (for auto-mapped samples)"
    )
    source: str = Field(
        default="manual",
        description="How labels were assigned: 'manual', 'mapped', 'inferred'"
    )
    
    def get(self, dimension: str) -> Optional[Union[str, List[str]]]:
        """Get value(s) for a dimension."""
        return self.labels.get(dimension)
    
    def get_flat(self, dimension: str) -> List[str]:
        """Get values as a flat list."""
        val = self.labels.get(dimension)
        if val is None:
            return []
        return [val] if isinstance(val, str) else val
    
    def has(self, dimension: str, value: Optional[str] = None) -> bool:
        """Check if sample has a dimension (optionally with specific value)."""
        if dimension not in self.labels:
            return False
        if value is None:
            return True
        values = self.get_flat(dimension)
        return value in values
    
    def merge(self, other: "SampleTaxonomy") -> "SampleTaxonomy":
        """Merge with another taxonomy, other takes precedence."""
        merged_labels = {**self.labels}
        for dim, vals in other.labels.items():
            if dim in merged_labels:
                existing = merged_labels[dim]
                if isinstance(existing, list) and isinstance(vals, list):
                    merged_labels[dim] = list(set(existing + vals))
                else:
                    merged_labels[dim] = vals
            else:
                merged_labels[dim] = vals
        
        return SampleTaxonomy(
            labels=merged_labels,
            confidence=min(self.confidence, other.confidence),
            source="merged",
        )
    
    def matches_filter(self, filters: Dict[str, Union[str, List[str]]]) -> bool:
        """
        Check if this taxonomy matches the given filters.
        
        Filters use OR within a dimension, AND across dimensions.
        """
        for dim, required_values in filters.items():
            if dim not in self.labels:
                return False
            
            sample_values = self.get_flat(dim)
            required_list = [required_values] if isinstance(required_values, str) else required_values
            
            # OR within dimension: at least one required value must be present
            if not any(rv in sample_values for rv in required_list):
                return False
        
        return True
