from ...schema import TaxonomySpec, TaxonomyDimension, TaxonomyNode

# -------------------------------------------------------------------------

# CWE dimension - Common Weakness Enumeration (top categories)

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

