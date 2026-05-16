from pathlib import Path
from runtime.evals.suite import SuiteLoader

class TestSuiteLoader:
    """Tests for YAML suite loading."""
    
    def test_load_minimal_suite(self, tmp_path: Path):
        """Test loading minimal suite config."""
        config = """
name: test-suite
dataset: data.jsonl
graders:
  accuracy:
    kind: tool
    function: exact_match
gate:
  metric_key: accuracy
  op: gte
  value: 0.7
"""
        suite_path = tmp_path / "suite.yaml"
        suite_path.write_text(config)
        
        suite = SuiteLoader.load(suite_path)
        
        assert suite.name == "test-suite"
        assert suite.dataset == "data.jsonl"
        assert "accuracy" in suite.graders
        assert suite.gate.value == 0.7
    
    def test_env_interpolation(self, tmp_path: Path, monkeypatch):
        """Test environment variable interpolation."""
        monkeypatch.setenv("TEST_MODEL", "gpt-4")
        
        config = """
name: test
dataset: data.jsonl
target:
  model: ${TEST_MODEL}
graders:
  accuracy:
    kind: tool
    function: exact_match
gate:
  metric_key: accuracy
  op: gte
  value: 0.7
"""
        suite_path = tmp_path / "suite.yaml"
        suite_path.write_text(config)
        
        suite = SuiteLoader.load(suite_path)
        
        assert suite.target.model == "gpt-4"
    
    def test_env_default_value(self, tmp_path: Path):
        """Test environment variable with default."""
        config = """
name: test
dataset: data.jsonl
target:
  model: ${UNDEFINED_VAR:-default-model}
graders:
  accuracy:
    kind: tool
    function: exact_match
gate:
  metric_key: accuracy
  op: gte
  value: 0.7
"""
        suite_path = tmp_path / "suite.yaml"
        suite_path.write_text(config)
        
        suite = SuiteLoader.load(suite_path)
        
        assert suite.target.model == "default-model"
    
    def test_validation_errors(self, tmp_path: Path):
        """Test validation error detection."""
        # Missing required field
        config = """
name: test
graders:
  accuracy:
    kind: tool
    function: exact_match
gate:
  metric_key: accuracy
  op: gte
  value: 0.7
"""
        suite_path = tmp_path / "suite.yaml"
        suite_path.write_text(config)
        
        errors = SuiteLoader.validate(suite_path)
        
        assert len(errors) > 0
        assert any("dataset" in e.lower() for e in errors)
