from runtime.evals import Sample
from runtime.evals.graders import ToolGrader, GraderRegistry

class TestToolGraders:
    """Tests for tool-based graders."""
    
    def test_exact_match(self):
        """Test exact match grader."""
        sample = Sample(id="1", input="Q", ground_truth="Paris")
        grader = ToolGrader(function="exact_match", config={"case_sensitive": True})
        
        result = grader.grade(sample, "Paris")
        assert result.score == 1.0
        
        result = grader.grade(sample, "paris")
        assert result.score == 0.0  # Case sensitive when configured
    
    def test_exact_match_case_insensitive(self):
        """Test case-insensitive exact match."""
        sample = Sample(id="1", input="Q", ground_truth="Paris")
        grader = ToolGrader(function="exact_match", config={"case_sensitive": False})
        
        result = grader.grade(sample, "PARIS")
        assert result.score == 1.0
    
    def test_contains(self):
        """Test contains grader."""
        sample = Sample(id="1", input="Q", ground_truth="Paris")
        grader = ToolGrader(function="contains")
        
        result = grader.grade(sample, "The capital is Paris, France.")
        assert result.score == 1.0
        
        result = grader.grade(sample, "London is the answer")
        assert result.score == 0.0
    
    def test_regex_match(self):
        """Test regex grader."""
        sample = Sample(id="1", input="Q", ground_truth=r"\d{4}")
        grader = ToolGrader(function="regex")
        
        result = grader.grade(sample, "The year was 1945.")
        assert result.score == 1.0
        
        result = grader.grade(sample, "Long ago")
        assert result.score == 0.0
    
    def test_numeric_match(self):
        """Test numeric grader with tolerance."""
        sample = Sample(id="1", input="Q", ground_truth="3.14159")
        grader = ToolGrader(function="numeric", config={"tolerance": 0.01})
        
        result = grader.grade(sample, "3.14")
        assert result.score == 1.0
        
        result = grader.grade(sample, "3.0")
        assert result.score == 0.0
    
    def test_json_match(self):
        """Test JSON structure grader."""
        sample = Sample(id="1", input="Q", ground_truth='{"name": "Alice", "age": 30}')
        grader = ToolGrader(function="json_match")
        
        # Same content, different formatting
        result = grader.grade(sample, '{ "age": 30, "name": "Alice" }')
        assert result.score == 1.0
    
    def test_starts_with(self):
        """Test starts_with grader."""
        sample = Sample(id="1", input="Q", ground_truth="The")
        grader = ToolGrader(function="starts_with")
        
        result = grader.grade(sample, "The answer is 42")
        assert result.score == 1.0
        
        result = grader.grade(sample, "Answer is 42")
        assert result.score == 0.0
    
    def test_grader_registry(self):
        """Test grader registry functions."""
        funcs = GraderRegistry.list_tool_functions()
        assert "exact_match" in funcs
        assert "contains" in funcs
        assert "regex" in funcs
