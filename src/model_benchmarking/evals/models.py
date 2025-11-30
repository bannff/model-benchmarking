"""
Pydantic models for the evals framework.

Defines the core data structures:
- Sample: A single test case from a dataset
- GradeResult: Score and rationale from grading
- SampleResult: Complete result for one sample evaluation
- Metrics: Aggregate metrics across all samples
- RunnerResult: Complete evaluation run result
- Configuration specs: GraderSpec, ExtractorSpec, GateSpec, TargetSpec, SuiteSpec
"""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator


# -----------------------------------------------------------------------------
# Enums
# -----------------------------------------------------------------------------


class GraderKind(str, Enum):
    """Type of grader to use."""
    TOOL = "tool"
    RUBRIC = "rubric"
    CUSTOM = "custom"


class Aggregation(str, Enum):
    """How to aggregate scores for metrics."""
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    ACCURACY = "accuracy"  # % of scores >= threshold
    PASS_RATE = "pass_rate"  # % of scores == 1.0


class GateOperator(str, Enum):
    """Comparison operators for gates."""
    GTE = "gte"  # >=
    GT = "gt"    # >
    LTE = "lte"  # <=
    LT = "lt"    # <
    EQ = "eq"    # ==


# -----------------------------------------------------------------------------
# Core Data Models
# -----------------------------------------------------------------------------


class Sample(BaseModel):
    """A single test case from a dataset."""
    
    id: Union[int, str] = Field(description="Unique identifier for this sample")
    input: str = Field(description="The prompt/question to send to the model")
    ground_truth: Optional[str] = Field(
        default=None,
        description="Expected answer (required for tool graders like exact_match/contains)"
    )
    context: Optional[str] = Field(
        default=None,
        description="Additional context to include with the prompt"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Override system prompt for this sample"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata (e.g., difficulty, source)"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for filtering samples"
    )
    rubric_vars: Dict[str, Any] = Field(
        default_factory=dict,
        description="Variables to interpolate into rubric prompts"
    )
    taxonomy: Optional[Dict[str, Union[str, List[str]]]] = Field(
        default=None,
        description="Taxonomy labels for this sample (dimension -> value(s))"
    )

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v: Any) -> Union[int, str]:
        """Allow both int and str IDs."""
        if isinstance(v, (int, str)):
            return v
        return str(v)
    
    def get_taxonomy_values(self, dimension: str) -> List[str]:
        """Get taxonomy values for a dimension as a list."""
        if self.taxonomy is None:
            return []
        val = self.taxonomy.get(dimension)
        if val is None:
            return []
        return [val] if isinstance(val, str) else val
    
    def has_taxonomy(self, dimension: str, value: Optional[str] = None) -> bool:
        """Check if sample has taxonomy label for dimension (optionally with specific value)."""
        if self.taxonomy is None or dimension not in self.taxonomy:
            return False
        if value is None:
            return True
        return value in self.get_taxonomy_values(dimension)


class GradeResult(BaseModel):
    """Result from grading a submission."""
    
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Numeric score between 0.0 and 1.0"
    )
    rationale: Optional[str] = Field(
        default=None,
        description="Explanation of the grading decision"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional grading metadata"
    )


class SampleResult(BaseModel):
    """Complete result for a single sample evaluation."""
    
    sample: Sample = Field(description="The original sample")
    response: str = Field(description="Raw model response")
    submission: str = Field(description="Extracted submission (after extractor)")
    grade: GradeResult = Field(description="Primary grade result")
    grades: Optional[Dict[str, GradeResult]] = Field(
        default=None,
        description="Per-metric grades when using multiple graders"
    )
    model_name: str = Field(description="Name/ID of the model used")
    latency_ms: Optional[float] = Field(
        default=None,
        description="Response latency in milliseconds"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if evaluation failed"
    )


class MetricAggregate(BaseModel):
    """Aggregate metrics for a single grader/metric."""
    
    avg_score: float = Field(description="Average score (0.0 to 1.0)")
    min_score: float = Field(description="Minimum score")
    max_score: float = Field(description="Maximum score")
    pass_rate: float = Field(description="Percentage of scores == 1.0")
    count: int = Field(description="Number of samples graded")


class Metrics(BaseModel):
    """Aggregate metrics across all samples."""
    
    total: int = Field(description="Total number of samples")
    attempted: int = Field(description="Number successfully evaluated")
    failed: int = Field(description="Number that errored")
    avg_score: float = Field(description="Average score across attempted")
    pass_rate: float = Field(description="Percentage of perfect scores")
    by_metric: Dict[str, MetricAggregate] = Field(
        default_factory=dict,
        description="Per-metric aggregates"
    )
    by_tag: Dict[str, MetricAggregate] = Field(
        default_factory=dict,
        description="Aggregates grouped by sample tags"
    )
    by_taxonomy: Dict[str, Dict[str, MetricAggregate]] = Field(
        default_factory=dict,
        description="Aggregates grouped by taxonomy dimension -> value"
    )


class RunnerResult(BaseModel):
    """Complete evaluation run result."""
    
    suite_name: str = Field(description="Name of the evaluation suite")
    model_name: str = Field(description="Model evaluated")
    provider_name: str = Field(description="Provider used")
    started_at: str = Field(description="ISO timestamp when run started")
    finished_at: str = Field(description="ISO timestamp when run finished")
    results: List[SampleResult] = Field(description="Results for each sample")
    metrics: Metrics = Field(description="Aggregate metrics")
    gate_passed: bool = Field(description="Whether the gate criteria were met")
    gate_details: Optional[str] = Field(
        default=None,
        description="Details about gate evaluation"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration used for this run"
    )


# -----------------------------------------------------------------------------
# Configuration Specs
# -----------------------------------------------------------------------------


class ExtractorSpec(BaseModel):
    """Configuration for content extraction."""
    
    name: str = Field(
        default="last_assistant",
        description="Extractor name (last_assistant, all_text, json_field, tool_calls)"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extractor-specific configuration"
    )


class ToolGraderSpec(BaseModel):
    """Configuration for tool-based graders."""
    
    kind: Literal[GraderKind.TOOL] = GraderKind.TOOL
    function: str = Field(
        description="Grading function (exact_match, contains, regex, custom)"
    )
    extractor: ExtractorSpec = Field(
        default_factory=lambda: ExtractorSpec(name="last_assistant"),
        description="How to extract submission from response"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Function-specific configuration (e.g., regex pattern)"
    )
    display_name: Optional[str] = Field(
        default=None,
        description="Human-readable name for this grader"
    )


class RubricGraderSpec(BaseModel):
    """Configuration for LLM-as-judge rubric graders."""
    
    kind: Literal[GraderKind.RUBRIC] = GraderKind.RUBRIC
    prompt: Optional[str] = Field(
        default=None,
        description="Inline rubric prompt"
    )
    prompt_file: Optional[str] = Field(
        default=None,
        description="Path to rubric prompt file"
    )
    model: str = Field(
        default="gpt-4o-mini",
        description="Model to use as judge"
    )
    provider: Optional[str] = Field(
        default=None,
        description="Provider for judge model (defaults to target provider)"
    )
    temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Temperature for judge model"
    )
    extractor: ExtractorSpec = Field(
        default_factory=lambda: ExtractorSpec(name="last_assistant"),
        description="How to extract submission from response"
    )
    rubric_vars: List[str] = Field(
        default_factory=list,
        description="Variables expected in sample.rubric_vars"
    )
    display_name: Optional[str] = Field(
        default=None,
        description="Human-readable name for this grader"
    )


class CustomGraderSpec(BaseModel):
    """Configuration for custom graders loaded from Python modules."""
    
    kind: Literal[GraderKind.CUSTOM] = GraderKind.CUSTOM
    module: str = Field(
        description="Python module path (e.g., my_graders:code_executes)"
    )
    extractor: ExtractorSpec = Field(
        default_factory=lambda: ExtractorSpec(name="last_assistant"),
        description="How to extract submission from response"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration passed to the custom grader"
    )
    display_name: Optional[str] = Field(
        default=None,
        description="Human-readable name for this grader"
    )


# Union type for grader specs
GraderSpec = Union[ToolGraderSpec, RubricGraderSpec, CustomGraderSpec]


class GateSpec(BaseModel):
    """Pass/fail criteria for an evaluation."""
    
    metric_key: str = Field(
        default="default",
        description="Which metric to evaluate (or 'default' for primary)"
    )
    aggregation: Aggregation = Field(
        default=Aggregation.AVG,
        description="How to aggregate scores"
    )
    op: GateOperator = Field(
        default=GateOperator.GTE,
        description="Comparison operator"
    )
    value: float = Field(
        description="Threshold value to compare against"
    )
    pass_threshold: Optional[float] = Field(
        default=None,
        description="Score threshold for 'accuracy' aggregation (default: 1.0)"
    )


class TargetSpec(BaseModel):
    """Target model/provider configuration."""
    
    provider: str = Field(
        default="ollama",
        description="Provider name (ollama, mock, strands-ollama, openai, etc.)"
    )
    model: str = Field(
        default="llama3.2",
        description="Model name/ID"
    )
    host: Optional[str] = Field(
        default=None,
        description="Provider host URL (for Ollama, etc.)"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key (can use ${ENV_VAR} syntax)"
    )
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Generation temperature"
    )
    max_tokens: int = Field(
        default=1024,
        gt=0,
        description="Maximum tokens to generate"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Default system prompt for all samples"
    )
    # Multi-model support
    models: Optional[List[str]] = Field(
        default=None,
        description="List of models to compare (overrides single 'model')"
    )


class SuiteSpec(BaseModel):
    """Complete evaluation suite configuration."""
    
    name: str = Field(description="Suite name")
    description: Optional[str] = Field(
        default=None,
        description="Suite description"
    )
    dataset: str = Field(
        description="Path to JSONL dataset file"
    )
    target: TargetSpec = Field(
        default_factory=TargetSpec,
        description="Target model configuration"
    )
    graders: Dict[str, GraderSpec] = Field(
        description="Named graders (metric_name -> grader config)"
    )
    gate: GateSpec = Field(
        description="Pass/fail criteria"
    )
    max_samples: Optional[int] = Field(
        default=None,
        gt=0,
        description="Maximum samples to evaluate"
    )
    sample_tags: Optional[List[str]] = Field(
        default=None,
        description="Only evaluate samples with these tags"
    )
    taxonomy_filter: Optional[Dict[str, Union[str, List[str]]]] = Field(
        default=None,
        description="Filter samples by taxonomy (dimension -> value(s))"
    )
    taxonomy_mapper: Optional[str] = Field(
        default=None,
        description="Taxonomy mapper to apply: 'cs_eval', 'cybergym', 'cve_bench', or path to YAML"
    )
    auto_taxonomy: bool = Field(
        default=False,
        description="Automatically infer taxonomy labels for samples"
    )
    max_concurrent: int = Field(
        default=5,
        gt=0,
        description="Maximum concurrent evaluations"
    )
    timeout: float = Field(
        default=60.0,
        gt=0,
        description="Timeout per sample in seconds"
    )
    
    # Internal field for path resolution
    base_dir: Optional[Path] = Field(
        default=None,
        exclude=True,
        description="Base directory for relative paths"
    )
    
    @field_validator("graders", mode="before")
    @classmethod
    def parse_graders(cls, v: Any) -> Dict[str, GraderSpec]:
        """Parse grader specs with discriminated union."""
        if not isinstance(v, dict):
            raise ValueError("graders must be a dict")
        
        result = {}
        for key, spec in v.items():
            if isinstance(spec, BaseModel):
                result[key] = spec
                continue
            
            if not isinstance(spec, dict):
                raise ValueError(f"Grader '{key}' must be a dict")
            
            kind = spec.get("kind", "tool")
            if kind == "tool":
                result[key] = ToolGraderSpec(**spec)
            elif kind == "rubric":
                result[key] = RubricGraderSpec(**spec)
            elif kind == "custom":
                result[key] = CustomGraderSpec(**spec)
            else:
                raise ValueError(f"Unknown grader kind: {kind}")
        
        return result
