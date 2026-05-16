from runtime.taxonomy import TaxonomyMapper, MappingRule, create_cs_eval_mapper, get_taxonomy

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
