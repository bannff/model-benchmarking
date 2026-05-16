from runtime.taxonomy import TaxonomyMapper, MappingRule, create_cs_eval_mapper

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
