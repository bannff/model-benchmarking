import pytest
import json
from pathlib import Path
from unittest.mock import Mock
from runtime.evals import SuiteSpec, GateSpec
from runtime.evals.runner import EvalRunner

class TestRunner:
    """Tests for evaluation runner."""
    
    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider that works with async execution."""
        provider = Mock()
        provider.model = "test-model"
        # Use a regular return value - the runner will use run_in_executor for sync methods
        provider.generate_text = Mock(return_value="Paris")
        # Mark that we don't have an async version
        provider.generate_text_async = None
        return provider
    
    @pytest.fixture
    def sample_suite(self, tmp_path: Path) -> SuiteSpec:
        """Create a test suite."""
        # Create dataset
        data = [
            {"id": "1", "input": "Capital of France?", "ground_truth": "Paris"},
            {"id": "2", "input": "Capital of UK?", "ground_truth": "London"},
        ]
        dataset_path = tmp_path / "data.jsonl"
        with open(dataset_path, "w") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")
        
        return SuiteSpec(
            name="test-suite",
            dataset=str(dataset_path),
            graders={
                "accuracy": {
                    "kind": "tool",
                    "function": "exact_match",
                }
            },
            gate=GateSpec(metric_key="accuracy", op="gte", value=0.5),
        )
    
    @pytest.mark.asyncio
    async def test_runner_basic(self, sample_suite: SuiteSpec, mock_provider):
        """Test basic runner execution."""
        runner = EvalRunner(sample_suite, mock_provider, verbose=False)
        result = await runner.run()
        
        assert result.suite_name == "test-suite"
        assert result.model_name == "test-model"
        assert len(result.results) == 2
        assert result.metrics.total == 2
    
    @pytest.mark.asyncio
    async def test_runner_gate_pass(self, sample_suite: SuiteSpec, mock_provider):
        """Test runner with passing gate."""
        runner = EvalRunner(sample_suite, mock_provider)
        result = await runner.run()
        
        # Mock returns "Paris" for both, so 1/2 = 50% which passes gte 0.5
        assert result.gate_passed
    
    def test_runner_sync(self, sample_suite: SuiteSpec, mock_provider):
        """Test synchronous runner wrapper."""
        # We need to use a new mock here because the sync runner will call it
        runner = EvalRunner(sample_suite, mock_provider)
        result = runner.run_sync()
        
        assert result.suite_name == "test-suite"
        assert len(result.results) == 2
