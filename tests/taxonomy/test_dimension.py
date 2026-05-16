from runtime.taxonomy import TaxonomyNode, TaxonomyDimension

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
