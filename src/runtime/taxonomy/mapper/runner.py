from __future__ import annotations
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from pathlib import Path
import yaml
from ..schema import TaxonomySpec, TaxonomyNode, SampleTaxonomy
from ..registry.core import get_taxonomy
from .rules import MappingRule

class TaxonomyMapper:

    """
    Maps samples to taxonomy labels using configurable rules.
    
    Usage:
        mapper = TaxonomyMapper("cybersecurity")
        mapper.add_rule(MappingRule("domain", "web", field="category", exact="Web Security"))
        taxonomy = mapper.map(sample_dict)
    """
    
    def __init__(
        self,
        taxonomy_name: str = "cybersecurity",
        taxonomy: Optional[TaxonomySpec] = None,
    ):
        self.taxonomy = taxonomy or get_taxonomy(taxonomy_name)
        if self.taxonomy is None:
            raise ValueError(f"Taxonomy not found: {taxonomy_name}")
        
        self.rules: List[MappingRule] = []
    
    def add_rule(self, rule: MappingRule) -> "TaxonomyMapper":
        """Add a mapping rule. Returns self for chaining."""
        self.rules.append(rule)
        # Keep sorted by priority (highest first)
        self.rules.sort(key=lambda r: -r.priority)
        return self
    
    def add_rules(self, rules: List[MappingRule]) -> "TaxonomyMapper":
        """Add multiple rules."""
        for rule in rules:
            self.add_rule(rule)
        return self
    
    def map(self, sample: Dict[str, Any]) -> SampleTaxonomy:
        """
        Map a sample to taxonomy labels.
        
        Args:
            sample: Sample dict with fields to match against
            
        Returns:
            SampleTaxonomy with matched labels
        """
        labels: Dict[str, List[str]] = {}
        
        for rule in self.rules:
            if rule.matches(sample):
                dim = rule.dimension
                if dim not in labels:
                    labels[dim] = []
                if rule.target_value not in labels[dim]:
                    labels[dim].append(rule.target_value)
        
        # Flatten single-value dimensions
        final_labels: Dict[str, Union[str, List[str]]] = {}
        for dim_id, values in labels.items():
            dim = self.taxonomy.dimensions.get(dim_id) if self.taxonomy else None
            if dim and not dim.multi_select and len(values) == 1:
                final_labels[dim_id] = values[0]
            else:
                final_labels[dim_id] = values
        
        return SampleTaxonomy(
            labels=final_labels,
            confidence=1.0,
            source="mapped",
        )
    
    @classmethod
    def from_yaml(cls, path: Union[str, Path], taxonomy_name: str = "cybersecurity") -> "TaxonomyMapper":
        """
        Load mapping rules from a YAML file.
        
        YAML format:
        ```yaml
        rules:
          - dimension: capability
            target: exploit_development
            field: category
            exact: ["Exploit", "Exploitation"]
          
          - dimension: domain
            target: web
            field: category
            contains: ["Web", "HTTP"]
        ```
        """
        config_path = Path(path)
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        mapper = cls(taxonomy_name)
        
        for rule_data in data.get("rules", []):
            rule = MappingRule(
                dimension=rule_data["dimension"],
                target_value=rule_data["target"],
                field=rule_data.get("field"),
                pattern=rule_data.get("pattern"),
                exact=rule_data.get("exact"),
                contains=rule_data.get("contains"),
                priority=rule_data.get("priority", 0),
            )
            mapper.add_rule(rule)
        
        return mapper


