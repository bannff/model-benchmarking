from __future__ import annotations
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from .rules import MappingRule
from .runner import TaxonomyMapper

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
