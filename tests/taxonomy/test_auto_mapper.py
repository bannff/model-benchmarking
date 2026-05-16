from runtime.taxonomy import AutoMapper, SampleTaxonomy

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
