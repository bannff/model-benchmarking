"""
Pydantic models for validating configuration and producing a resolved config.

These models provide structure and early error reporting for pipeline and suites.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


from .constants import (
    DEFAULT_OLLAMA_HOST,
    DEFAULT_MODEL,
    DEFAULT_CYBERGYM_SERVER,
    DEFAULT_OUTPUT_DIR,
)


class ProviderConfig(BaseModel):
    name: Literal["ollama", "strands-ollama", "mock"] = Field(default="ollama")
    model: str = Field(default=DEFAULT_MODEL)
    host: Optional[str] = Field(default=DEFAULT_OLLAMA_HOST)


class PipelineConfig(BaseModel):
    categories: Optional[List[str]] = None
    max_questions: Optional[int] = None
    output_dir: Path = Field(default=DEFAULT_OUTPUT_DIR)
    verbose: bool = Field(default=False)
    use_strands_telemetry: bool = Field(default=False)
    skip_cs_eval: bool = Field(default=False)
    skip_cybergym: bool = Field(default=False)
    skip_cve_bench: bool = Field(default=False)

    @field_validator("max_questions")
    @classmethod
    def _validate_max_questions(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("max_questions must be > 0 if provided")
        return v

    @field_validator("output_dir")
    @classmethod
    def validate_output_dir(cls, v: Path) -> Path:
        if v.exists() and not os.access(v, os.W_OK):
            raise ValueError(f"Output directory '{v}' is not writable")
        # If it doesn't exist, we assume it can be created, 
        # but check parent if possible
        if not v.exists() and v.parent.exists() and not os.access(v.parent, os.W_OK):
            raise ValueError(f"Parent of output directory '{v}' is not writable")
        return v


class CSEvalConfig(BaseModel):
    local_sample_path: Optional[Path] = None

    @field_validator("local_sample_path")
    @classmethod
    def validate_local_sample_path(cls, v: Optional[Path]) -> Optional[Path]:
        if v is not None and not v.exists():
            raise ValueError(f"Local sample path '{v}' does not exist")
        return v


class CyberGymConfig(BaseModel):
    mode: Literal["sim", "server"] = Field(default="sim")
    server_url: str = Field(default=DEFAULT_CYBERGYM_SERVER)
    data_dir: Optional[Path] = None
    difficulty: str = Field(default="level1")


class CVEBenchConfig(BaseModel):
    repo_root: Optional[Path] = None
    model: Optional[str] = None
    targets: List[str] = Field(default_factory=list)


class RootConfig(BaseModel):
    provider: ProviderConfig = Field(default_factory=ProviderConfig)
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)
    cs_eval: CSEvalConfig = Field(default_factory=CSEvalConfig)
    cybergym: CyberGymConfig = Field(default_factory=CyberGymConfig)
    cvebench: CVEBenchConfig = Field(default_factory=CVEBenchConfig)


def validate_config(raw: dict) -> RootConfig:
    """Validate and coerce a raw dict into a RootConfig instance."""
    return RootConfig.model_validate(raw or {})


def merge_and_validate(base: dict, override: dict) -> RootConfig:
    """Deep-merge two dicts, with override taking precedence, then validate."""
    from .config import deep_merge

    merged = deep_merge(base or {}, override or {})
    return validate_config(merged)
