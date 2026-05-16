from runtime.taxonomy import TaxonomyNode, TaxonomyDimension, TaxonomySpec

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
