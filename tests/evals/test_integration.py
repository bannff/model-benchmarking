import json
from pathlib import Path
from unittest.mock import Mock
from runtime.evals.suite import load_suite
from runtime.evals.runner import EvalRunner

class TestIntegration:
    """End-to-end integration tests."""
    
    def test_full_pipeline(self, tmp_path: Path):
        """Test complete eval pipeline from YAML config."""
        # Create dataset
        data = [
            {"id": "1", "input": "What is 2+2?", "ground_truth": "4"},
            {"id": "2", "input": "What is 3+3?", "ground_truth": "6"},
        ]
        dataset_path = tmp_path / "data.jsonl"
        with open(dataset_path, "w") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")
        
        # Create suite config
        config = f"""
name: math-test
dataset: {dataset_path}
graders:
  accuracy:
    kind: tool
    function: contains
    config:
      case_sensitive: false
gate:
  metric_key: accuracy
  op: gte
  value: 0.5
max_samples: 10
"""
        suite_path = tmp_path / "suite.yaml"
        suite_path.write_text(config)
        
        # Mock provider that gives correct answers
        provider = Mock()
        provider.model = "test"
        provider.generate_text = Mock(side_effect=lambda x: "4" if "2+2" in x else "6")
        # Mark that we don't have async version
        provider.generate_text_async = None
        
        # Run evaluation
        suite = load_suite(suite_path)
        runner = EvalRunner(suite, provider)
        result = runner.run_sync()
        
        assert result.gate_passed
        assert result.metrics.avg_score == 1.0
