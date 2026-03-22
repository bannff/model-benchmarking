from __future__ import annotations
from ...schema import TaxonomySpec
from .cyber_capability import capability_dim
from .cyber_domain import domain_dim
from .cyber_difficulty import difficulty_dim
from .cyber_cwe import cwe_dim
from .cyber_attack import attack_stage_dim
from .cyber_eval import eval_type_dim

def get_cybersecurity_taxonomy() -> TaxonomySpec:

    return TaxonomySpec(
        name="cybersecurity",
        version="1.0.0",
        description="Comprehensive cybersecurity evaluation taxonomy aligned with industry standards (CWE, MITRE ATT&CK)",
        dimensions={
            "capability": capability_dim,
            "domain": domain_dim,
            "difficulty": difficulty_dim,
            "cwe": cwe_dim,
            "attack_stage": attack_stage_dim,
            "eval_type": eval_type_dim,
        },
    )
