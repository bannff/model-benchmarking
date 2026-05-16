from runtime.taxonomy import MappingRule

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
