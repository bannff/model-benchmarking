from __future__ import annotations

import pytest

from runtime.config_models import (
    RootConfig,
    merge_and_validate,
)


def test_invalid_max_questions_raises():
    raw = {
        "pipeline": {
            "max_questions": 0,
        }
    }
    with pytest.raises(ValueError):
        RootConfig.model_validate(raw)


def test_invalid_provider_name_raises():
    raw = {
        "provider": {
            "name": "not-a-provider"
        }
    }
    with pytest.raises(Exception):  # pydantic will raise a validation error
        RootConfig.model_validate(raw)


def test_merge_and_validate_merges_and_validates():
    base = {
        "provider": {"name": "ollama", "model": "llama3.2"},
        "pipeline": {"output_dir": "results", "verbose": False},
    }
    override = {
        "pipeline": {"max_questions": 5, "skip_cs_eval": True}
    }
    cfg = merge_and_validate(base, override)
    assert cfg.pipeline.max_questions == 5
    assert cfg.pipeline.skip_cs_eval is True
    assert cfg.provider.name == "ollama"
