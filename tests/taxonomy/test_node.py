from runtime.taxonomy import TaxonomyNode

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
