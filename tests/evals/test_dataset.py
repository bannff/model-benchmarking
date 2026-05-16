import json
from pathlib import Path
from runtime.evals.dataset import load_dataset, load_dataset_list

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
