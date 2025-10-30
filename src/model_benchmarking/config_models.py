"""
Pydantic models for validating configuration and producing a resolved config.

These models provide structure and early error reporting for pipeline and suites.
"""
from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class ProviderConfig(BaseModel):
    name: Literal["ollama", "strands-ollama", "mock"] = Field(default="ollama")
    model: str = Field(default="llama3.2")
    host: Optional[str] = Field(default="http://localhost:11434")


class PipelineConfig(BaseModel):
    categories: Optional[List[str]] = None
    max_questions: Optional[int] = None
    output_dir: str = Field(default="results")
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


class CSEvalConfig(BaseModel):
    local_sample_path: Optional[str] = None


class CyberGymConfig(BaseModel):
    mode: Literal["sim", "server"] = Field(default="sim")
    server_url: str = Field(default="http://localhost:8666")
    data_dir: Optional[str] = None
    difficulty: str = Field(default="level1")


class CVEBenchConfig(BaseModel):
    repo_root: Optional[str] = None
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
