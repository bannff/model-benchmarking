from ...schema import TaxonomySpec, TaxonomyDimension, TaxonomyNode

# -------------------------------------------------------------------------

# Domain dimension - Security area/domain

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

