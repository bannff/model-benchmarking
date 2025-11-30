"""
Taxonomy registry for loading, storing, and accessing taxonomies.

Provides:
- Built-in cybersecurity taxonomy
- Loading from YAML files
- Global registry for taxonomy access
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml

from .schema import (
    TaxonomySpec,
    TaxonomyDimension,
    TaxonomyNode,
)


class TaxonomyRegistry:
    """
    Global registry for taxonomy specifications.
    
    Manages loading, caching, and access to taxonomy definitions.
    """
    
    _instance: Optional["TaxonomyRegistry"] = None
    _taxonomies: Dict[str, TaxonomySpec]
    
    def __new__(cls) -> "TaxonomyRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._taxonomies = {}
            cls._instance._load_builtins()
        return cls._instance
    
    def _load_builtins(self) -> None:
        """Load built-in taxonomies."""
        self._taxonomies["cybersecurity"] = _create_cybersecurity_taxonomy()
    
    def register(self, taxonomy: TaxonomySpec) -> None:
        """Register a taxonomy specification."""
        self._taxonomies[taxonomy.name] = taxonomy
    
    def get(self, name: str) -> Optional[TaxonomySpec]:
        """Get a taxonomy by name."""
        return self._taxonomies.get(name)
    
    def list(self) -> List[str]:
        """List all registered taxonomy names."""
        return list(self._taxonomies.keys())
    
    def load_from_file(self, path: Union[str, Path]) -> TaxonomySpec:
        """
        Load a taxonomy from a YAML file.
        
        Args:
            path: Path to YAML taxonomy definition
            
        Returns:
            Loaded and registered TaxonomySpec
        """
        config_path = Path(path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Taxonomy file not found: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        taxonomy = TaxonomySpec.model_validate(data)
        self.register(taxonomy)
        return taxonomy
    
    def load_from_dict(self, data: Dict[str, Any]) -> TaxonomySpec:
        """Load a taxonomy from a dictionary."""
        taxonomy = TaxonomySpec.model_validate(data)
        self.register(taxonomy)
        return taxonomy
    
    def clear(self) -> None:
        """Clear all registered taxonomies (for testing)."""
        self._taxonomies.clear()
        self._load_builtins()


# Convenience functions
def get_taxonomy(name: str = "cybersecurity") -> Optional[TaxonomySpec]:
    """Get a taxonomy by name from the global registry."""
    return TaxonomyRegistry().get(name)


def list_taxonomies() -> List[str]:
    """List all registered taxonomy names."""
    return TaxonomyRegistry().list()


def register_taxonomy(taxonomy: TaxonomySpec) -> None:
    """Register a taxonomy in the global registry."""
    TaxonomyRegistry().register(taxonomy)


def _create_cybersecurity_taxonomy() -> TaxonomySpec:
    """
    Create the built-in cybersecurity taxonomy.
    
    Dimensions:
    - capability: What skill/ability is being tested
    - domain: Security domain/area
    - difficulty: Normalized difficulty levels
    - cwe: Common Weakness Enumeration
    - attack_stage: MITRE ATT&CK kill chain stage
    """
    
    # -------------------------------------------------------------------------
    # Capability dimension - What skill is being evaluated
    # -------------------------------------------------------------------------
    capability_nodes = [
        TaxonomyNode(
            id="vulnerability_analysis",
            name="Vulnerability Analysis",
            description="Identifying and understanding security vulnerabilities",
            aliases=["vuln_analysis", "vulnerability_assessment"],
            children=[
                TaxonomyNode(
                    id="code_review",
                    name="Code Review",
                    description="Finding vulnerabilities through source code analysis",
                    aliases=["source_code_review", "code_audit"],
                ),
                TaxonomyNode(
                    id="binary_analysis",
                    name="Binary Analysis",
                    description="Analyzing compiled binaries for vulnerabilities",
                    aliases=["reverse_engineering", "binary_reversing"],
                ),
                TaxonomyNode(
                    id="configuration_review",
                    name="Configuration Review",
                    description="Identifying misconfigurations",
                    aliases=["config_review", "config_audit"],
                ),
            ],
        ),
        TaxonomyNode(
            id="exploit_development",
            name="Exploit Development",
            description="Creating exploits for vulnerabilities",
            aliases=["exploitation", "exploit_writing"],
            children=[
                TaxonomyNode(
                    id="buffer_overflow",
                    name="Buffer Overflow",
                    description="Memory corruption exploitation",
                    aliases=["bof", "memory_corruption"],
                    children=[
                        TaxonomyNode(id="stack_overflow", name="Stack Overflow", aliases=["stack_bof"]),
                        TaxonomyNode(id="heap_overflow", name="Heap Overflow", aliases=["heap_bof"]),
                        TaxonomyNode(id="format_string", name="Format String", aliases=["fmt_string"]),
                    ],
                ),
                TaxonomyNode(
                    id="web_exploitation",
                    name="Web Exploitation",
                    description="Exploiting web application vulnerabilities",
                    aliases=["web_exploit"],
                    children=[
                        TaxonomyNode(id="sqli", name="SQL Injection", aliases=["sql_injection"]),
                        TaxonomyNode(id="xss", name="Cross-Site Scripting", aliases=["cross_site_scripting"]),
                        TaxonomyNode(id="ssrf", name="Server-Side Request Forgery", aliases=["server_side_request_forgery"]),
                        TaxonomyNode(id="rce", name="Remote Code Execution", aliases=["remote_code_execution"]),
                    ],
                ),
                TaxonomyNode(
                    id="privilege_escalation",
                    name="Privilege Escalation",
                    description="Escalating access privileges",
                    aliases=["privesc", "priv_esc"],
                ),
            ],
        ),
        TaxonomyNode(
            id="incident_response",
            name="Incident Response",
            description="Responding to security incidents",
            aliases=["ir", "security_incident_response"],
            children=[
                TaxonomyNode(id="detection", name="Detection", aliases=["threat_detection"]),
                TaxonomyNode(id="containment", name="Containment", aliases=["threat_containment"]),
                TaxonomyNode(id="eradication", name="Eradication", aliases=["threat_eradication"]),
                TaxonomyNode(id="recovery", name="Recovery", aliases=["system_recovery"]),
            ],
        ),
        TaxonomyNode(
            id="forensics",
            name="Digital Forensics",
            description="Investigating security incidents and analyzing evidence",
            aliases=["digital_forensics", "computer_forensics"],
            children=[
                TaxonomyNode(id="memory_forensics", name="Memory Forensics", aliases=["ram_forensics"]),
                TaxonomyNode(id="disk_forensics", name="Disk Forensics", aliases=["storage_forensics"]),
                TaxonomyNode(id="network_forensics", name="Network Forensics", aliases=["packet_analysis"]),
                TaxonomyNode(id="log_analysis", name="Log Analysis", aliases=["log_forensics"]),
            ],
        ),
        TaxonomyNode(
            id="secure_coding",
            name="Secure Coding",
            description="Writing secure code and fixing vulnerabilities",
            aliases=["secure_development", "secure_programming"],
            children=[
                TaxonomyNode(id="input_validation", name="Input Validation", aliases=["input_sanitization"]),
                TaxonomyNode(id="output_encoding", name="Output Encoding", aliases=["output_sanitization"]),
                TaxonomyNode(id="authentication", name="Authentication", aliases=["authn"]),
                TaxonomyNode(id="authorization", name="Authorization", aliases=["authz"]),
            ],
        ),
        TaxonomyNode(
            id="cryptography",
            name="Cryptography",
            description="Understanding and applying cryptographic concepts",
            aliases=["crypto"],
            children=[
                TaxonomyNode(id="encryption", name="Encryption", aliases=["symmetric_crypto", "asymmetric_crypto"]),
                TaxonomyNode(id="hashing", name="Hashing", aliases=["hash_functions"]),
                TaxonomyNode(id="key_management", name="Key Management", aliases=["key_handling"]),
                TaxonomyNode(id="crypto_attacks", name="Cryptographic Attacks", aliases=["crypto_breaking"]),
            ],
        ),
        TaxonomyNode(
            id="security_operations",
            name="Security Operations",
            description="Operating and maintaining security systems",
            aliases=["secops", "soc"],
            children=[
                TaxonomyNode(id="monitoring", name="Monitoring", aliases=["security_monitoring"]),
                TaxonomyNode(id="alerting", name="Alerting", aliases=["alert_management"]),
                TaxonomyNode(id="threat_hunting", name="Threat Hunting", aliases=["proactive_detection"]),
            ],
        ),
    ]
    
    capability_dim = TaxonomyDimension(
        id="capability",
        name="Capability",
        description="The security skill or ability being evaluated",
        required=False,
        multi_select=True,
        nodes=capability_nodes,
    )
    
    # -------------------------------------------------------------------------
    # Domain dimension - Security area/domain
    # -------------------------------------------------------------------------
    domain_nodes = [
        TaxonomyNode(
            id="network",
            name="Network Security",
            description="Network-layer security",
            aliases=["network_security", "netsec"],
            children=[
                TaxonomyNode(id="firewall", name="Firewall", aliases=["fw"]),
                TaxonomyNode(id="ids_ips", name="IDS/IPS", aliases=["intrusion_detection", "intrusion_prevention"]),
                TaxonomyNode(id="vpn", name="VPN", aliases=["virtual_private_network"]),
                TaxonomyNode(id="dns", name="DNS Security", aliases=["dns_sec"]),
            ],
        ),
        TaxonomyNode(
            id="web",
            name="Web Security",
            description="Web application security",
            aliases=["web_security", "web_app_security", "appsec"],
        ),
        TaxonomyNode(
            id="cloud",
            name="Cloud Security",
            description="Cloud infrastructure security",
            aliases=["cloud_security", "cloud_sec"],
            children=[
                TaxonomyNode(id="aws", name="AWS Security", aliases=["amazon_web_services"]),
                TaxonomyNode(id="azure", name="Azure Security", aliases=["microsoft_azure"]),
                TaxonomyNode(id="gcp", name="GCP Security", aliases=["google_cloud"]),
                TaxonomyNode(id="kubernetes", name="Kubernetes Security", aliases=["k8s_security", "container_orchestration"]),
            ],
        ),
        TaxonomyNode(
            id="binary",
            name="Binary/System Security",
            description="Low-level system and binary security",
            aliases=["system_security", "binary_security", "systems"],
        ),
        TaxonomyNode(
            id="mobile",
            name="Mobile Security",
            description="Mobile application and device security",
            aliases=["mobile_security", "mobile_sec"],
            children=[
                TaxonomyNode(id="android", name="Android Security", aliases=["android_sec"]),
                TaxonomyNode(id="ios", name="iOS Security", aliases=["ios_sec", "apple_security"]),
            ],
        ),
        TaxonomyNode(
            id="database",
            name="Database Security",
            description="Database and data storage security",
            aliases=["database_security", "db_security", "data_security"],
        ),
        TaxonomyNode(
            id="iot",
            name="IoT Security",
            description="Internet of Things device security",
            aliases=["iot_security", "embedded_security"],
        ),
        TaxonomyNode(
            id="identity",
            name="Identity & Access Management",
            description="Identity, authentication, and authorization",
            aliases=["iam", "identity_management", "access_management"],
        ),
    ]
    
    domain_dim = TaxonomyDimension(
        id="domain",
        name="Domain",
        description="The security domain or area",
        required=False,
        multi_select=True,
        nodes=domain_nodes,
    )
    
    # -------------------------------------------------------------------------
    # Difficulty dimension - Normalized difficulty levels
    # -------------------------------------------------------------------------
    difficulty_nodes = [
        TaxonomyNode(
            id="level0",
            name="Level 0 - Trivial",
            description="Basic recall, simple lookups",
            aliases=["trivial", "beginner"],
        ),
        TaxonomyNode(
            id="level1",
            name="Level 1 - Easy",
            description="Single-step problems, basic concepts",
            aliases=["easy", "simple"],
        ),
        TaxonomyNode(
            id="level2",
            name="Level 2 - Medium",
            description="Multi-step problems, combined concepts",
            aliases=["medium", "intermediate"],
        ),
        TaxonomyNode(
            id="level3",
            name="Level 3 - Hard",
            description="Complex problems requiring deep understanding",
            aliases=["hard", "advanced"],
        ),
        TaxonomyNode(
            id="level4",
            name="Level 4 - Expert",
            description="Novel problems requiring creative solutions",
            aliases=["expert", "very_hard"],
        ),
        TaxonomyNode(
            id="level5",
            name="Level 5 - Research",
            description="Open research problems",
            aliases=["research", "cutting_edge"],
        ),
    ]
    
    difficulty_dim = TaxonomyDimension(
        id="difficulty",
        name="Difficulty",
        description="Normalized difficulty level",
        required=False,
        multi_select=False,
        nodes=difficulty_nodes,
    )
    
    # -------------------------------------------------------------------------
    # CWE dimension - Common Weakness Enumeration (top categories)
    # -------------------------------------------------------------------------
    cwe_nodes = [
        TaxonomyNode(
            id="cwe_79",
            name="CWE-79: XSS",
            description="Improper Neutralization of Input During Web Page Generation",
            aliases=["xss", "cross_site_scripting"],
            metadata={"cwe_id": 79},
        ),
        TaxonomyNode(
            id="cwe_89",
            name="CWE-89: SQL Injection",
            description="Improper Neutralization of Special Elements used in an SQL Command",
            aliases=["sqli", "sql_injection"],
            metadata={"cwe_id": 89},
        ),
        TaxonomyNode(
            id="cwe_119",
            name="CWE-119: Buffer Errors",
            description="Improper Restriction of Operations within the Bounds of a Memory Buffer",
            aliases=["buffer_overflow", "memory_corruption"],
            metadata={"cwe_id": 119},
        ),
        TaxonomyNode(
            id="cwe_200",
            name="CWE-200: Information Exposure",
            description="Exposure of Sensitive Information to an Unauthorized Actor",
            aliases=["info_disclosure", "information_leak"],
            metadata={"cwe_id": 200},
        ),
        TaxonomyNode(
            id="cwe_287",
            name="CWE-287: Authentication Issues",
            description="Improper Authentication",
            aliases=["auth_bypass", "authentication_bypass"],
            metadata={"cwe_id": 287},
        ),
        TaxonomyNode(
            id="cwe_352",
            name="CWE-352: CSRF",
            description="Cross-Site Request Forgery",
            aliases=["csrf", "xsrf"],
            metadata={"cwe_id": 352},
        ),
        TaxonomyNode(
            id="cwe_434",
            name="CWE-434: Unrestricted Upload",
            description="Unrestricted Upload of File with Dangerous Type",
            aliases=["file_upload", "unrestricted_upload"],
            metadata={"cwe_id": 434},
        ),
        TaxonomyNode(
            id="cwe_502",
            name="CWE-502: Deserialization",
            description="Deserialization of Untrusted Data",
            aliases=["insecure_deserialization", "deserialization"],
            metadata={"cwe_id": 502},
        ),
        TaxonomyNode(
            id="cwe_918",
            name="CWE-918: SSRF",
            description="Server-Side Request Forgery",
            aliases=["ssrf", "server_side_request_forgery"],
            metadata={"cwe_id": 918},
        ),
        TaxonomyNode(
            id="cwe_22",
            name="CWE-22: Path Traversal",
            description="Improper Limitation of a Pathname to a Restricted Directory",
            aliases=["path_traversal", "directory_traversal", "lfi"],
            metadata={"cwe_id": 22},
        ),
    ]
    
    cwe_dim = TaxonomyDimension(
        id="cwe",
        name="CWE",
        description="Common Weakness Enumeration classification",
        required=False,
        multi_select=True,
        nodes=cwe_nodes,
    )
    
    # -------------------------------------------------------------------------
    # Attack Stage dimension - MITRE ATT&CK kill chain stages
    # -------------------------------------------------------------------------
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
    
    # -------------------------------------------------------------------------
    # Evaluation Type dimension - What kind of evaluation
    # -------------------------------------------------------------------------
    eval_type_nodes = [
        TaxonomyNode(
            id="knowledge",
            name="Knowledge",
            description="Testing factual knowledge and recall",
            aliases=["factual", "recall"],
        ),
        TaxonomyNode(
            id="reasoning",
            name="Reasoning",
            description="Testing logical reasoning and problem-solving",
            aliases=["logic", "problem_solving"],
        ),
        TaxonomyNode(
            id="practical",
            name="Practical",
            description="Hands-on task execution",
            aliases=["hands_on", "execution"],
        ),
        TaxonomyNode(
            id="creative",
            name="Creative",
            description="Novel solution generation",
            aliases=["novel", "innovative"],
        ),
    ]
    
    eval_type_dim = TaxonomyDimension(
        id="eval_type",
        name="Evaluation Type",
        description="The type of evaluation being performed",
        required=False,
        multi_select=False,
        nodes=eval_type_nodes,
    )
    
    # -------------------------------------------------------------------------
    # Build the complete taxonomy
    # -------------------------------------------------------------------------
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
