"""
Tests for the taxonomy module.
"""
from model_benchmarking.taxonomy import (
    TaxonomyNode,
    TaxonomyDimension,
    TaxonomySpec,
    SampleTaxonomy,
    get_taxonomy,
    list_taxonomies,
    TaxonomyMapper,
    MappingRule,
    AutoMapper,
    create_cs_eval_mapper,
)


class TestTaxonomyNode:
    """Tests for TaxonomyNode."""
    
    def test_create_simple_node(self):
        """Test creating a simple node."""
        node = TaxonomyNode(id="test", name="Test Node")
        assert node.id == "test"
        assert node.name == "Test Node"
        assert node.children == []
        assert node.aliases == []
    
    def test_create_node_with_children(self):
        """Test creating a node with children."""
        child1 = TaxonomyNode(id="child1", name="Child 1")
        child2 = TaxonomyNode(id="child2", name="Child 2")
        parent = TaxonomyNode(id="parent", name="Parent", children=[child1, child2])
        
        assert len(parent.children) == 2
        assert parent.children[0].id == "child1"
    
    def test_id_normalization(self):
        """Test that IDs are normalized."""
        node = TaxonomyNode(id="Test-Node", name="Test")
        assert node.id == "test_node"
    
    def test_flatten(self):
        """Test flattening a node hierarchy."""
        child = TaxonomyNode(id="child", name="Child")
        parent = TaxonomyNode(id="parent", name="Parent", children=[child])
        
        flattened = parent.flatten()
        assert "parent" in flattened
        assert "parent.child" in flattened
    
    def test_get_all_aliases(self):
        """Test getting all aliases."""
        node = TaxonomyNode(
            id="web_security",
            name="Web Security",
            aliases=["websec", "appsec"]
        )
        aliases = node.get_all_aliases()
        
        assert "web_security" in aliases
        assert "web security" in aliases
        assert "websec" in aliases
        assert "appsec" in aliases


class TestTaxonomyDimension:
    """Tests for TaxonomyDimension."""
    
    def test_create_dimension(self):
        """Test creating a dimension."""
        nodes = [
            TaxonomyNode(id="node1", name="Node 1"),
            TaxonomyNode(id="node2", name="Node 2"),
        ]
        dim = TaxonomyDimension(
            id="test_dim",
            name="Test Dimension",
            nodes=nodes
        )
        
        assert dim.id == "test_dim"
        assert len(dim.nodes) == 2
    
    def test_get_valid_values(self):
        """Test getting valid values."""
        child = TaxonomyNode(id="child", name="Child")
        parent = TaxonomyNode(id="parent", name="Parent", children=[child])
        dim = TaxonomyDimension(id="test", name="Test", nodes=[parent])
        
        values = dim.get_valid_values()
        assert "parent" in values
        assert "parent.child" in values
    
    def test_validate_value(self):
        """Test validating a value."""
        node = TaxonomyNode(id="valid", name="Valid")
        dim = TaxonomyDimension(id="test", name="Test", nodes=[node])
        
        assert dim.validate_value("valid") is True
        assert dim.validate_value("invalid") is False


class TestSampleTaxonomy:
    """Tests for SampleTaxonomy."""
    
    def test_create_sample_taxonomy(self):
        """Test creating sample taxonomy."""
        tax = SampleTaxonomy(labels={"domain": "web", "difficulty": "level1"})
        
        assert tax.get("domain") == "web"
        assert tax.get("nonexistent") is None
    
    def test_get_flat(self):
        """Test getting values as flat list."""
        tax = SampleTaxonomy(labels={
            "capability": ["exploit_development", "vulnerability_analysis"],
            "domain": "web"
        })
        
        assert tax.get_flat("capability") == ["exploit_development", "vulnerability_analysis"]
        assert tax.get_flat("domain") == ["web"]
        assert tax.get_flat("missing") == []
    
    def test_has(self):
        """Test has method."""
        tax = SampleTaxonomy(labels={"domain": ["web", "network"]})
        
        assert tax.has("domain") is True
        assert tax.has("domain", "web") is True
        assert tax.has("domain", "cloud") is False
        assert tax.has("missing") is False
    
    def test_matches_filter(self):
        """Test filter matching."""
        tax = SampleTaxonomy(labels={
            "domain": "web",
            "capability": ["exploit_development", "vulnerability_analysis"]
        })
        
        # Match single value
        assert tax.matches_filter({"domain": "web"}) is True
        assert tax.matches_filter({"domain": "network"}) is False
        
        # Match with list (OR within dimension)
        assert tax.matches_filter({"domain": ["web", "network"]}) is True
        
        # Match multiple dimensions (AND across)
        assert tax.matches_filter({"domain": "web", "capability": "exploit_development"}) is True
        assert tax.matches_filter({"domain": "web", "capability": "forensics"}) is False
    
    def test_merge(self):
        """Test merging taxonomies."""
        tax1 = SampleTaxonomy(labels={"domain": "web"})
        tax2 = SampleTaxonomy(labels={"capability": "exploit_development"})
        
        merged = tax1.merge(tax2)
        assert merged.get("domain") == "web"
        assert merged.get("capability") == "exploit_development"


class TestTaxonomySpec:
    """Tests for TaxonomySpec."""
    
    def test_create_spec(self):
        """Test creating a taxonomy spec."""
        dim = TaxonomyDimension(
            id="domain",
            name="Domain",
            nodes=[TaxonomyNode(id="web", name="Web")]
        )
        spec = TaxonomySpec(
            name="test",
            version="1.0.0",
            dimensions={"domain": dim}
        )
        
        assert spec.name == "test"
        assert "domain" in spec.dimensions
    
    def test_validate_labels(self):
        """Test label validation."""
        dim = TaxonomyDimension(
            id="domain",
            name="Domain",
            required=True,
            nodes=[TaxonomyNode(id="web", name="Web")]
        )
        spec = TaxonomySpec(name="test", dimensions={"domain": dim})
        
        # Valid
        errors = spec.validate_labels({"domain": "web"})
        assert len(errors) == 0
        
        # Missing required
        errors = spec.validate_labels({})
        assert len(errors) == 1
        assert "required" in errors[0].lower()
        
        # Invalid value
        errors = spec.validate_labels({"domain": "invalid"})
        assert len(errors) == 1


class TestTaxonomyRegistry:
    """Tests for TaxonomyRegistry."""
    
    def test_builtin_cybersecurity_taxonomy(self):
        """Test that the built-in cybersecurity taxonomy exists."""
        tax = get_taxonomy("cybersecurity")
        
        assert tax is not None
        assert tax.name == "cybersecurity"
        assert "capability" in tax.dimensions
        assert "domain" in tax.dimensions
        assert "difficulty" in tax.dimensions
        assert "cwe" in tax.dimensions
        assert "attack_stage" in tax.dimensions
    
    def test_list_taxonomies(self):
        """Test listing taxonomies."""
        taxonomies = list_taxonomies()
        assert "cybersecurity" in taxonomies
    
    def test_capability_dimension(self):
        """Test capability dimension has expected nodes."""
        tax = get_taxonomy("cybersecurity")
        assert tax is not None
        
        cap_dim = tax.dimensions["capability"]
        valid_values = cap_dim.get_valid_values()
        
        assert "exploit_development" in valid_values
        assert "vulnerability_analysis" in valid_values
        assert "forensics" in valid_values
    
    def test_cwe_dimension(self):
        """Test CWE dimension has expected nodes."""
        tax = get_taxonomy("cybersecurity")
        assert tax is not None
        
        cwe_dim = tax.dimensions["cwe"]
        valid_values = cwe_dim.get_valid_values()
        
        assert "cwe_79" in valid_values
        assert "cwe_89" in valid_values
        assert "cwe_119" in valid_values


class TestMappingRule:
    """Tests for MappingRule."""
    
    def test_exact_match(self):
        """Test exact matching."""
        rule = MappingRule(
            dimension="domain",
            target_value="web",
            field="category",
            exact="Web Security"
        )
        
        assert rule.matches({"category": "Web Security"}) is True
        assert rule.matches({"category": "Network Security"}) is False
    
    def test_contains_match(self):
        """Test contains matching."""
        rule = MappingRule(
            dimension="domain",
            target_value="web",
            field="category",
            contains=["Web", "HTTP"]
        )
        
        assert rule.matches({"category": "Web Security"}) is True
        assert rule.matches({"category": "HTTP API"}) is True
        assert rule.matches({"category": "Network"}) is False
    
    def test_pattern_match(self):
        """Test regex pattern matching."""
        rule = MappingRule(
            dimension="cwe",
            target_value="cwe_79",
            field="description",
            pattern=r"xss|cross.?site.?script"
        )
        
        assert rule.matches({"description": "XSS vulnerability"}) is True
        assert rule.matches({"description": "Cross-Site Scripting"}) is True
        assert rule.matches({"description": "SQL Injection"}) is False
    
    def test_custom_function(self):
        """Test custom function matching."""
        rule = MappingRule(
            dimension="difficulty",
            target_value="level3",
            func=lambda s: s.get("score", 0) > 80
        )
        
        assert rule.matches({"score": 90}) is True
        assert rule.matches({"score": 50}) is False
    
    def test_nested_field(self):
        """Test matching on nested fields."""
        rule = MappingRule(
            dimension="domain",
            target_value="web",
            field="metadata.type",
            exact="web"
        )
        
        assert rule.matches({"metadata": {"type": "web"}}) is True
        assert rule.matches({"metadata": {"type": "network"}}) is False


class TestTaxonomyMapper:
    """Tests for TaxonomyMapper."""
    
    def test_create_mapper(self):
        """Test creating a mapper."""
        mapper = TaxonomyMapper("cybersecurity")
        assert mapper.taxonomy is not None
    
    def test_add_and_apply_rules(self):
        """Test adding and applying rules."""
        mapper = TaxonomyMapper("cybersecurity")
        mapper.add_rule(MappingRule(
            dimension="domain",
            target_value="web",
            field="category",
            exact="Web Security"
        ))
        
        result = mapper.map({"category": "Web Security"})
        # Domain is multi-select, so it returns a list
        assert "web" in result.get_flat("domain")
    
    def test_cs_eval_mapper(self):
        """Test CS-Eval mapper."""
        mapper = create_cs_eval_mapper()
        
        # Test domain mapping
        result = mapper.map({"category": "Network Security"})
        assert "network" in result.get_flat("domain")
        
        # Test capability mapping
        result = mapper.map({"category": "Cryptography"})
        assert "cryptography" in result.get_flat("capability")
        
        # Test default eval_type
        result = mapper.map({"category": "Any"})
        assert result.get("eval_type") == "knowledge"


class TestAutoMapper:
    """Tests for AutoMapper."""
    
    def test_create_auto_mapper(self):
        """Test creating an auto mapper."""
        mapper = AutoMapper(taxonomy_name="cybersecurity")
        assert mapper.taxonomy is not None
    
    def test_infer_from_text(self):
        """Test inferring taxonomy from text."""
        mapper = AutoMapper(taxonomy_name="cybersecurity", min_confidence=0.3)
        
        # Test with XSS-related text
        sample = {
            "input": "Explain how to prevent XSS attacks in web applications"
        }
        result = mapper.infer(sample)
        
        # Should detect web domain
        assert len(result.labels) > 0
    
    def test_infer_from_vulnerability_description(self):
        """Test inferring from vulnerability description."""
        mapper = AutoMapper(taxonomy_name="cybersecurity", min_confidence=0.3)
        
        sample = {
            "vulnerability_description": "Buffer overflow in the heap memory allocator"
        }
        result = mapper.infer(sample)
        
        # Should have some inferences
        assert result.source == "inferred"
    
    def test_enrich_existing(self):
        """Test enriching existing taxonomy."""
        mapper = AutoMapper(taxonomy_name="cybersecurity", min_confidence=0.3)
        
        existing = SampleTaxonomy(labels={"domain": "web"})
        sample = {"input": "SQL injection attack prevention"}
        
        enriched = mapper.enrich(sample, existing)
        
        # Should preserve existing
        assert enriched.get("domain") == "web"
        assert enriched.source == "enriched"


class TestIntegration:
    """Integration tests for the taxonomy module."""
    
    def test_end_to_end_mapping(self):
        """Test complete mapping workflow."""
        # Create mapper with custom rules
        mapper = TaxonomyMapper("cybersecurity")
        mapper.add_rules([
            MappingRule(
                dimension="domain",
                target_value="web",
                field="category",
                contains=["Web", "HTTP", "API"]
            ),
            MappingRule(
                dimension="capability",
                target_value="exploit_development",
                field="type",
                exact="exploit"
            ),
            MappingRule(
                dimension="eval_type",
                target_value="practical",
                func=lambda s: s.get("requires_execution", False)
            ),
        ])
        
        # Map a sample
        sample: dict[str, object] = {
            "id": "test-1",
            "category": "Web Security",
            "type": "exploit",
            "requires_execution": True,
            "input": "Develop an XSS exploit"
        }
        
        result = mapper.map(sample)
        
        # Multi-select dimensions return lists
        assert "web" in result.get_flat("domain")
        assert "exploit_development" in result.get_flat("capability")
        # Single-select dimension (eval_type) returns single value when only one match
        assert result.get("eval_type") == "practical"
        assert result.source == "mapped"
    
    def test_taxonomy_validation_with_mapped_labels(self):
        """Test that mapped labels pass validation."""
        mapper = create_cs_eval_mapper()
        tax = get_taxonomy("cybersecurity")
        assert tax is not None
        
        result = mapper.map({"category": "Network Security"})
        errors = tax.validate_labels(result.labels)
        
        # Mapped labels should be valid
        assert len(errors) == 0
