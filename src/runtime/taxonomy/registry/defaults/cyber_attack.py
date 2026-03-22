from ...schema import TaxonomySpec, TaxonomyDimension, TaxonomyNode

# -------------------------------------------------------------------------

# Attack Stage dimension - MITRE ATT&CK kill chain stages

attack_stage_nodes = [
    TaxonomyNode(
        id="reconnaissance",
        name="Reconnaissance",
        description="Gathering information about the target",
        aliases=["recon", "information_gathering"],
        metadata={"mitre_tactic": "TA0043"},
    ),
    TaxonomyNode(
        id="initial_access",
        name="Initial Access",
        description="Gaining initial foothold",
        aliases=["foothold", "entry_point"],
        metadata={"mitre_tactic": "TA0001"},
    ),
    TaxonomyNode(
        id="execution",
        name="Execution",
        description="Running malicious code",
        aliases=["code_execution"],
        metadata={"mitre_tactic": "TA0002"},
    ),
    TaxonomyNode(
        id="persistence",
        name="Persistence",
        description="Maintaining access",
        aliases=["backdoor", "maintain_access"],
        metadata={"mitre_tactic": "TA0003"},
    ),
    TaxonomyNode(
        id="privilege_escalation",
        name="Privilege Escalation",
        description="Gaining higher privileges",
        aliases=["privesc", "elevation"],
        metadata={"mitre_tactic": "TA0004"},
    ),
    TaxonomyNode(
        id="defense_evasion",
        name="Defense Evasion",
        description="Avoiding detection",
        aliases=["evasion", "stealth"],
        metadata={"mitre_tactic": "TA0005"},
    ),
    TaxonomyNode(
        id="lateral_movement",
        name="Lateral Movement",
        description="Moving through the network",
        aliases=["pivoting", "network_movement"],
        metadata={"mitre_tactic": "TA0008"},
    ),
    TaxonomyNode(
        id="exfiltration",
        name="Exfiltration",
        description="Stealing data",
        aliases=["data_theft", "data_exfil"],
        metadata={"mitre_tactic": "TA0010"},
    ),
    TaxonomyNode(
        id="impact",
        name="Impact",
        description="Disrupting or destroying systems/data",
        aliases=["destruction", "disruption"],
        metadata={"mitre_tactic": "TA0040"},
    ),
]

attack_stage_dim = TaxonomyDimension(
    id="attack_stage",
    name="Attack Stage",
    description="MITRE ATT&CK kill chain stage",
    required=False,
    multi_select=True,
    nodes=attack_stage_nodes,
)

