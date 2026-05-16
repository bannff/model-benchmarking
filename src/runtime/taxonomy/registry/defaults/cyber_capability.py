from ...schema import TaxonomySpec, TaxonomyDimension, TaxonomyNode

# -------------------------------------------------------------------------

# Capability dimension - What skill is being evaluated

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

