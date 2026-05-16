"""
Tests for configuration validation logic.
"""
import pytest
import os
from pathlib import Path
from runtime.config_models import PipelineConfig, CSEvalConfig

def test_output_dir_writability(tmp_path):
    """Verify that read-only output directories are rejected."""
    ro_dir = tmp_path / "read_only"
    ro_dir.mkdir()
    os.chmod(ro_dir, 0o555)  # Read & Execute only
    
    with pytest.raises(ValueError, match="is not writable"):
        PipelineConfig(output_dir=str(ro_dir))

def test_local_sample_path_existence():
    """Verify that missing local sample paths are rejected."""
    with pytest.raises(ValueError, match="does not exist"):
        CSEvalConfig(local_sample_path="/non/existent/path.jsonl")

def test_valid_config(tmp_path):
    """Verify that valid configs pass."""
    writable_dir = tmp_path / "writable"
    writable_dir.mkdir()
    
    config = PipelineConfig(output_dir=str(writable_dir))
    assert config.output_dir == str(writable_dir)
