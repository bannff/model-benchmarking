"""
Tests for the evals framework core components.

Tests cover:
- Dataset loading
- Extractors
- Tool graders
- Gates
- Suite loading
- Runner execution
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock

from runtime.evals import (
    Sample,
    GradeResult,
    SampleResult,
    Metrics,
    RunnerResult,
    SuiteSpec,
    GateSpec,
    ExtractorSpec,
)
from runtime.evals.dataset import load_dataset, load_dataset_list
from runtime.evals.extractors import (
    ExtractorRegistry,
    get_extractor,
    LastAssistantExtractor,
    JsonFieldExtractor,
    RegexCaptureExtractor,
    CodeBlockExtractor,
)
from runtime.evals.graders import (
    ToolGrader,
    TOOL_GRADER_FUNCTIONS,
    GraderRegistry,
)
from runtime.evals.gates import GateEvaluator, calculate_metrics, check_gate
from runtime.evals.suite import SuiteLoader, load_suite
from runtime.evals.runner import EvalRunner


# =============================================================================
# Dataset Tests
# =============================================================================


class TestDataset:
    """Tests for dataset loading."""
    
    def test_load_jsonl(self, tmp_path: Path):
        """Test loading JSONL dataset."""
        data = [
            {"id": "1", "input": "Q1?", "ground_truth": "A1"},
            {"id": "2", "input": "Q2?", "ground_truth": "A2"},
        ]
        file_path = tmp_path / "test.jsonl"
        with open(file_path, "w") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")
        
        samples = list(load_dataset(file_path))
        
        assert len(samples) == 2
        assert samples[0].id == "1"
        assert samples[0].input == "Q1?"
        assert samples[1].ground_truth == "A2"
    
    def test_load_with_max_samples(self, tmp_path: Path):
        """Test limiting samples."""
        data = [{"id": str(i), "input": f"Q{i}", "ground_truth": f"A{i}"} for i in range(10)]
        file_path = tmp_path / "test.jsonl"
        with open(file_path, "w") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")
        
        samples = load_dataset_list(file_path, max_samples=3)
        
        assert len(samples) == 3
    
    def test_load_with_tags_filter(self, tmp_path: Path):
        """Test filtering by tags."""
        data = [
            {"id": "1", "input": "Q1", "ground_truth": "A1", "tags": ["math"]},
            {"id": "2", "input": "Q2", "ground_truth": "A2", "tags": ["science"]},
            {"id": "3", "input": "Q3", "ground_truth": "A3", "tags": ["math", "advanced"]},
        ]
        file_path = tmp_path / "test.jsonl"
        with open(file_path, "w") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")
        
        samples = load_dataset_list(file_path, sample_tags=["math"])
        
        assert len(samples) == 2
        assert all("math" in s.tags for s in samples)


# =============================================================================
# Extractor Tests
# =============================================================================


class TestExtractors:
    """Tests for response extractors."""
    
    def test_last_assistant_plain(self):
        """Test extracting from plain text."""
        ext = LastAssistantExtractor()
        result = ext.extract("The answer is 42.")
        assert result == "The answer is 42."
    
    def test_last_assistant_chat_format(self):
        """Test extracting from chat format."""
        ext = LastAssistantExtractor()
        response = "User: What is 2+2?\nAssistant: 4\nUser: Thanks!\nAssistant: You're welcome!"
        result = ext.extract(response)
        assert result == "You're welcome!"
    
    def test_json_field_basic(self):
        """Test JSON field extraction."""
        ext = JsonFieldExtractor(config={"field": "answer"})
        response = '{"answer": "Paris", "confidence": 0.9}'
        result = ext.extract(response)
        assert result == "Paris"
    
    def test_json_field_nested(self):
        """Test nested JSON field extraction."""
        ext = JsonFieldExtractor(config={"field": "result.value"})
        response = '{"result": {"value": 42, "unit": "meters"}}'
        result = ext.extract(response)
        assert result == "42"
    
    def test_json_field_in_markdown(self):
        """Test JSON in markdown code block."""
        ext = JsonFieldExtractor(config={"field": "answer"})
        response = "Here's the answer:\n```json\n{\"answer\": \"42\"}\n```"
        result = ext.extract(response)
        assert result == "42"
    
    def test_regex_capture(self):
        """Test regex capture extraction."""
        ext = RegexCaptureExtractor(config={"pattern": r"Answer:\s*(.+)"})
        response = "The question was easy.\nAnswer: 42\nThat's it."
        result = ext.extract(response)
        assert result == "42"
    
    def test_regex_capture_with_flags(self):
        """Test regex with case-insensitive flag."""
        ext = RegexCaptureExtractor(config={"pattern": r"answer:\s*(\w+)", "flags": "i"})
        response = "ANSWER: Paris"
        result = ext.extract(response)
        assert result == "Paris"
    
    def test_code_block_python(self):
        """Test Python code block extraction."""
        ext = CodeBlockExtractor(config={"language": "python"})
        response = "Here's the code:\n```python\ndef hello():\n    print('Hi')\n```"
        result = ext.extract(response)
        assert "def hello():" in result
        assert "print('Hi')" in result
    
    def test_registry_list(self):
        """Test listing extractors."""
        extractors = ExtractorRegistry.list_extractors()
        assert "last_assistant" in extractors
        assert "json_field" in extractors
        assert "regex" in extractors
    
    def test_registry_create(self):
        """Test creating extractor from spec."""
        spec = ExtractorSpec(name="json_field", config={"field": "answer"})
        ext = ExtractorRegistry.create(spec)
        assert isinstance(ext, JsonFieldExtractor)


# =============================================================================
# Grader Tests
# =============================================================================


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


# =============================================================================
# Gate Tests
# =============================================================================


class TestGates:
    """Tests for pass/fail gates."""
    
    def _make_results(self, scores: list[float]) -> list[SampleResult]:
        """Helper to create sample results."""
        return [
            SampleResult(
                sample=Sample(id=str(i), input="Q", ground_truth="A"),
                response="R",
                submission="S",
                grade=GradeResult(score=score),
                model_name="test",
            )
            for i, score in enumerate(scores)
        ]
    
    def test_gte_pass(self):
        """Test greater-than-or-equal gate passing."""
        results = self._make_results([0.8, 0.9, 0.7, 0.85])
        gate = GateSpec(metric_key="accuracy", op="gte", value=0.7)
        
        passed, details = check_gate(gate, results)
        
        assert passed
        assert "0.81" in details  # Average score
    
    def test_gte_fail(self):
        """Test greater-than-or-equal gate failing."""
        results = self._make_results([0.5, 0.6, 0.4, 0.5])
        gate = GateSpec(metric_key="accuracy", op="gte", value=0.7)
        
        passed, details = check_gate(gate, results)
        
        assert not passed
    
    def test_gt_pass(self):
        """Test greater-than gate."""
        results = self._make_results([0.8, 0.9])
        gate = GateSpec(metric_key="accuracy", op="gt", value=0.8)
        
        passed, _ = check_gate(gate, results)
        assert passed
    
    def test_eq_pass(self):
        """Test equality gate."""
        results = self._make_results([1.0, 1.0, 1.0])
        gate = GateSpec(metric_key="accuracy", op="eq", value=1.0)
        
        passed, _ = check_gate(gate, results)
        assert passed
    
    def test_calculate_metrics(self):
        """Test metrics calculation."""
        results = self._make_results([1.0, 0.5, 0.0, 1.0])
        
        metrics = calculate_metrics(results)
        
        assert metrics.total == 4
        assert metrics.attempted == 4
        assert metrics.avg_score == 0.625
        assert metrics.pass_rate == 0.5  # 2 passed (score == 1.0)


# =============================================================================
# Suite Tests
# =============================================================================


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


# =============================================================================
# Runner Tests
# =============================================================================


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
        runner = EvalRunner(sample_suite, mock_provider)
        result = runner.run_sync()
        
        assert result.suite_name == "test-suite"
        assert len(result.results) == 2


# =============================================================================
# Integration Tests
# =============================================================================


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
