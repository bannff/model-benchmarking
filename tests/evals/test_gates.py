from runtime.evals import Sample, GradeResult, SampleResult, GateSpec
from runtime.evals.gates import calculate_metrics, check_gate

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
