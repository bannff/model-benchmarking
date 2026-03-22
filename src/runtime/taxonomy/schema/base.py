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


