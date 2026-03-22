from __future__ import annotations
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from ..schema import TaxonomySpec, TaxonomyNode, SampleTaxonomy
from ..registry.core import get_taxonomy

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
