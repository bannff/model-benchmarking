from runtime.taxonomy import SampleTaxonomy

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
