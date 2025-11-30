"""
Taxonomy mapper for classifying samples.

Provides:
- TaxonomyMapper: Manual mapping rules from sample fields to taxonomy labels
- AutoMapper: Automatic inference of taxonomy from sample content
"""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from pathlib import Path
import yaml

from .schema import TaxonomySpec, TaxonomyNode, SampleTaxonomy
from .registry import get_taxonomy


class MappingRule:
    """
    A rule for mapping sample fields to taxonomy labels.
    
    Rules can match on:
    - Exact field values
    - Regex patterns
    - Custom functions
    """
    
    def __init__(
        self,
        dimension: str,
        target_value: str,
        *,
        field: Optional[str] = None,
        pattern: Optional[str] = None,
        exact: Optional[Union[str, List[str]]] = None,
        contains: Optional[Union[str, List[str]]] = None,
        func: Optional[Callable[[Dict[str, Any]], bool]] = None,
        priority: int = 0,
    ):
        """
        Create a mapping rule.
        
        Args:
            dimension: Target taxonomy dimension (e.g., "capability")
            target_value: Value to assign if rule matches (e.g., "exploit_development")
            field: Sample field to check (e.g., "category", "metadata.type")
            pattern: Regex pattern to match
            exact: Exact value(s) to match
            contains: Substring(s) to check for
            func: Custom function taking sample dict, returning bool
            priority: Higher priority rules are checked first
        """
        self.dimension = dimension
        self.target_value = target_value
        self.field = field
        self.pattern = re.compile(pattern, re.IGNORECASE) if pattern else None
        self.exact = [exact] if isinstance(exact, str) else exact
        self.contains = [contains] if isinstance(contains, str) else contains
        self.func = func
        self.priority = priority
    
    def _get_field_value(self, sample: Dict[str, Any]) -> Optional[str]:
        """Get a field value from sample, supporting dot notation."""
        if not self.field:
            return None
        
        parts = self.field.split(".")
        value = sample
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
            
            if value is None:
                return None
        
        return str(value) if value is not None else None
    
    def matches(self, sample: Dict[str, Any]) -> bool:
        """Check if this rule matches the sample."""
        # Custom function takes priority
        if self.func is not None:
            return self.func(sample)
        
        # Get field value
        value = self._get_field_value(sample)
        if value is None:
            return False
        
        value_lower = value.lower()
        
        # Check exact match
        if self.exact:
            if any(e.lower() == value_lower for e in self.exact):
                return True
        
        # Check contains
        if self.contains:
            if any(c.lower() in value_lower for c in self.contains):
                return True
        
        # Check regex pattern
        if self.pattern:
            if self.pattern.search(value):
                return True
        
        return False


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


class AutoMapper:
    """
    Automatically infer taxonomy labels from sample content using fuzzy matching.
    
    Uses the taxonomy's aliases and node names to match against sample text.
    """
    
    def __init__(
        self,
        taxonomy: Optional[TaxonomySpec] = None,
        taxonomy_name: str = "cybersecurity",
        min_confidence: float = 0.5,
    ):
        self.taxonomy = taxonomy if taxonomy is not None else get_taxonomy(taxonomy_name)
        if self.taxonomy is None:
            raise ValueError(f"Taxonomy not found: {taxonomy_name}")
        
        self.min_confidence = min_confidence
        
        # Build lookup tables for each dimension
        self._lookup: Dict[str, List[Tuple[str, TaxonomyNode, List[str]]]] = {}
        
        for dim_id, dim in self.taxonomy.dimensions.items():
            entries: List[Tuple[str, TaxonomyNode, List[str]]] = []
            
            for node_path, node in dim.flatten().items():
                aliases = list(node.get_all_aliases())
                entries.append((node_path, node, aliases))
            
            self._lookup[dim_id] = entries
    
    def _find_matches(
        self,
        text: str,
        dimension: str,
    ) -> List[Tuple[str, float]]:
        """Find matching taxonomy values in text."""
        matches: List[Tuple[str, float]] = []
        text_lower = text.lower()
        
        entries = self._lookup.get(dimension, [])
        
        for node_path, _node, aliases in entries:
            for alias in aliases:
                # Check for word boundary match
                pattern = r"\b" + re.escape(alias) + r"\b"
                if re.search(pattern, text_lower):
                    # Confidence based on alias length (longer = more specific)
                    confidence = min(1.0, len(alias) / 20.0 + 0.5)
                    matches.append((node_path, confidence))
                    break  # Only match once per node
        
        return matches
    
    def infer(
        self,
        sample: Dict[str, Any],
        fields: Optional[List[str]] = None,
    ) -> SampleTaxonomy:
        """
        Infer taxonomy labels from sample content.
        
        Args:
            sample: Sample dict
            fields: Fields to analyze (default: input, question, context, ground_truth)
            
        Returns:
            SampleTaxonomy with inferred labels
        """
        if fields is None:
            fields = ["input", "question", "context", "ground_truth", "vulnerability_description", "prompt"]
        
        # Collect text from sample
        text_parts: List[str] = []
        
        for field in fields:
            value = sample.get(field)
            if isinstance(value, str):
                text_parts.append(value)
        
        combined_text = " ".join(text_parts)
        
        if not combined_text.strip():
            return SampleTaxonomy(labels={}, confidence=0.0, source="inferred")
        
        # Find matches for each dimension
        labels: Dict[str, Union[str, List[str]]] = {}
        confidences: List[float] = []
        
        assert self.taxonomy is not None
        for dim_id, dim in self.taxonomy.dimensions.items():
            matches = self._find_matches(combined_text, dim_id)
            
            # Filter by confidence threshold
            matches = [(v, c) for v, c in matches if c >= self.min_confidence]
            
            if matches:
                # Sort by confidence and take best
                matches.sort(key=lambda x: -x[1])
                
                if dim.multi_select:
                    labels[dim_id] = [m[0] for m in matches[:3]]  # Top 3
                    confidences.extend([m[1] for m in matches[:3]])
                else:
                    labels[dim_id] = matches[0][0]
                    confidences.append(matches[0][1])
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return SampleTaxonomy(
            labels=labels,
            confidence=avg_confidence,
            source="inferred",
        )
    
    def enrich(
        self,
        sample: Dict[str, Any],
        existing: Optional[SampleTaxonomy] = None,
    ) -> SampleTaxonomy:
        """
        Enrich existing taxonomy with inferred labels for missing dimensions.
        
        Args:
            sample: Sample dict
            existing: Existing taxonomy labels
            
        Returns:
            Merged SampleTaxonomy
        """
        inferred = self.infer(sample)
        
        if existing is None:
            return inferred
        
        # Only add inferred labels for dimensions not already set
        merged_labels = dict(existing.labels)
        
        for dim, value in inferred.labels.items():
            if dim not in merged_labels:
                merged_labels[dim] = value
        
        return SampleTaxonomy(
            labels=merged_labels,
            confidence=min(existing.confidence, inferred.confidence),
            source="enriched",
        )


# Convenience factory for common suite mappings
def create_cs_eval_mapper() -> TaxonomyMapper:
    """Create a mapper for CS-Eval categories."""
    mapper = TaxonomyMapper("cybersecurity")
    
    # Map CS-Eval categories to domains
    domain_mappings = [
        ("Network Security", "network"),
        ("Web Security", "web"),
        ("Cloud Security", "cloud"),
        ("Mobile Security", "mobile"),
        ("Database Security", "database"),
        ("System Security", "binary"),
        ("Software Security", "binary"),
    ]
    
    for category, domain in domain_mappings:
        mapper.add_rule(MappingRule(
            dimension="domain",
            target_value=domain,
            field="category",
            exact=category,
        ))
    
    # Map to capabilities
    capability_mappings = [
        ("Cryptography", "cryptography"),
        ("Digital Forensics", "forensics"),
        ("Risk Management", "security_operations"),
        ("Security Management", "security_operations"),
    ]
    
    for category, capability in capability_mappings:
        mapper.add_rule(MappingRule(
            dimension="capability",
            target_value=capability,
            field="category",
            exact=category,
        ))
    
    # Default eval type for CS-Eval (knowledge-based)
    mapper.add_rule(MappingRule(
        dimension="eval_type",
        target_value="knowledge",
        func=lambda s: True,  # Always apply
        priority=-1,  # Low priority default
    ))
    
    return mapper


def create_cybergym_mapper() -> TaxonomyMapper:
    """Create a mapper for CyberGym tasks."""
    mapper = TaxonomyMapper("cybersecurity")
    
    # CyberGym is practical exploitation
    mapper.add_rule(MappingRule(
        dimension="eval_type",
        target_value="practical",
        func=lambda s: True,
        priority=-1,
    ))
    
    mapper.add_rule(MappingRule(
        dimension="capability",
        target_value="exploit_development",
        func=lambda s: True,
        priority=-1,
    ))
    
    # Infer domain from vulnerability description
    mapper.add_rule(MappingRule(
        dimension="domain",
        target_value="web",
        field="vulnerability_description",
        contains=["web", "http", "html", "javascript", "xss", "sqli", "injection"],
    ))
    
    mapper.add_rule(MappingRule(
        dimension="domain",
        target_value="binary",
        field="vulnerability_description",
        contains=["buffer", "overflow", "memory", "heap", "stack", "binary", "elf"],
    ))
    
    return mapper


def create_cve_bench_mapper() -> TaxonomyMapper:
    """Create a mapper for CVE-Bench challenges."""
    mapper = TaxonomyMapper("cybersecurity")
    
    # CVE-Bench is practical
    mapper.add_rule(MappingRule(
        dimension="eval_type",
        target_value="practical",
        func=lambda s: True,
        priority=-1,
    ))
    
    mapper.add_rule(MappingRule(
        dimension="capability",
        target_value="vulnerability_analysis",
        func=lambda s: True,
        priority=-1,
    ))
    
    return mapper
