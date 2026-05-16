from __future__ import annotations
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

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


