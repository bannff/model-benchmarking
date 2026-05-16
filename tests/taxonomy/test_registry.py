from runtime.taxonomy import get_taxonomy, list_taxonomies

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
